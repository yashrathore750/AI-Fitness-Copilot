from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog import WORKOUT_MET_VALUES
from app.models import ActivityLog, FoodLog, NutritionReference, User
from app.schemas import AnalysisContext, DailyAnalysisResponse, Deficiency, InsightPayload, NutritionSummary
from app.services.fallback_coach import build_insights
from app.services.llm_insights import generate_llm_insights
from app.types import Goal

RDA_BASELINES = {
    "fiber": 25.0,
    "magnesium": 400.0,
}


def normalize_food_name(food_name: str) -> str:
    return food_name.strip().lower()


def day_bounds(target_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


async def get_user_or_404(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def list_food_logs(session: AsyncSession, user_id: int, target_date: date) -> list[FoodLog]:
    start, end = day_bounds(target_date)
    result = await session.scalars(
        select(FoodLog)
        .where(FoodLog.user_id == user_id)
        .where(FoodLog.logged_at >= start)
        .where(FoodLog.logged_at < end)
        .order_by(FoodLog.logged_at.asc())
    )
    return list(result.all())


async def list_activity_logs(session: AsyncSession, user_id: int, target_date: date) -> list[ActivityLog]:
    start, end = day_bounds(target_date)
    result = await session.scalars(
        select(ActivityLog)
        .where(ActivityLog.user_id == user_id)
        .where(ActivityLog.logged_at >= start)
        .where(ActivityLog.logged_at < end)
        .order_by(ActivityLog.logged_at.asc())
    )
    return list(result.all())


async def summarize_day(
    session: AsyncSession,
    *,
    user: User,
    food_logs: list[FoodLog],
    activity_logs: list[ActivityLog],
    target_date: date,
) -> NutritionSummary:
    food_names = {normalize_food_name(log.food_name) for log in food_logs}
    reference_rows = await session.scalars(
        select(NutritionReference).where(NutritionReference.food_name.in_(food_names))
    )
    reference_by_name = {row.food_name: row for row in reference_rows.all()}

    vitamins: dict[str, float] = defaultdict(float)
    minerals: dict[str, float] = defaultdict(float)
    calories_in = 0.0
    protein_g = 0.0
    carbs_g = 0.0
    fat_g = 0.0
    fiber_g = 0.0
    missing_foods: list[str] = []

    for log in food_logs:
        normalized_name = normalize_food_name(log.food_name)
        reference = reference_by_name.get(normalized_name)
        if reference is None:
            missing_foods.append(log.food_name)
            continue

        servings = log.servings
        calories_in += reference.calories * servings
        protein_g += reference.protein_g * servings
        carbs_g += reference.carbs_g * servings
        fat_g += reference.fat_g * servings
        fiber_g += reference.fiber_g * servings
        for name, value in reference.vitamins.items():
            vitamins[name] += value * servings
        for name, value in reference.minerals.items():
            minerals[name] += value * servings

    steps = sum(log.steps for log in activity_logs)
    workout_minutes = sum(log.duration_minutes for log in activity_logs)
    step_calories = steps * 0.04
    workout_calories = 0.0

    for log in activity_logs:
        if log.calories_burned_override is not None:
            workout_calories += log.calories_burned_override
            continue
        if log.duration_minutes <= 0 or not log.workout_type:
            continue
        met_value = WORKOUT_MET_VALUES.get(log.workout_type.strip().lower(), 4.0)
        workout_calories += met_value * user.weight_kg * (log.duration_minutes / 60)

    return NutritionSummary(
        date=target_date,
        calories_in=round(calories_in, 2),
        calories_out=round(step_calories + workout_calories, 2),
        protein_g=round(protein_g, 2),
        carbs_g=round(carbs_g, 2),
        fat_g=round(fat_g, 2),
        fiber_g=round(fiber_g, 2),
        vitamins={name: round(value, 2) for name, value in vitamins.items()},
        minerals={name: round(value, 2) for name, value in minerals.items()},
        steps=steps,
        workout_minutes=workout_minutes,
        foods_missing_from_catalog=missing_foods,
    )


def protein_target_for_goal(goal: Goal, weight_kg: float) -> float:
    multiplier = {
        Goal.FAT_LOSS: 1.8,
        Goal.MAINTENANCE: 1.4,
        Goal.MUSCLE_GAIN: 2.0,
        Goal.RECOMPOSITION: 2.0,
    }[goal]
    return weight_kg * multiplier


def severity_from_ratio(ratio: float) -> str:
    if ratio < 0.4:
        return "high"
    if ratio < 0.7:
        return "medium"
    return "low"


def detect_deficiencies(summary: NutritionSummary, user: User) -> list[Deficiency]:
    deficiencies: list[Deficiency] = []

    targets = {
        "fiber": (summary.fiber_g, RDA_BASELINES["fiber"], "g"),
        "magnesium": (summary.minerals.get("magnesium", 0.0), RDA_BASELINES["magnesium"], "mg"),
        "protein": (summary.protein_g, protein_target_for_goal(user.goal, user.weight_kg), "g"),
    }

    for name, (actual, target, unit) in targets.items():
        if actual >= target:
            continue
        ratio = actual / target if target else 0.0
        deficiencies.append(
            Deficiency(
                name=name,
                actual=round(actual, 2),
                target=round(target, 2),
                unit=unit,
                severity=severity_from_ratio(ratio),
            )
        )

    return deficiencies


def build_context(user: User, summary: NutritionSummary, deficiencies: list[Deficiency], activity_logs: list[ActivityLog]) -> AnalysisContext:
    workouts = [log.workout_type for log in activity_logs if log.workout_type]
    return AnalysisContext(
        user_goal=user.goal,
        diet_type=user.diet_type,
        activity={
            "steps": summary.steps,
            "workout_minutes": summary.workout_minutes,
            "workouts": workouts,
        },
        nutrition_summary=summary,
        deficiencies=deficiencies,
    )


def summary_for_balance(user: User, summary: NutritionSummary) -> str:
    calorie_balance = summary.calories_in - summary.calories_out
    if user.goal == Goal.FAT_LOSS and calorie_balance < 0:
        return "You maintained a calorie deficit today, which supports your fat-loss goal."
    if user.goal == Goal.MUSCLE_GAIN and calorie_balance > 0:
        return "You finished the day in a calorie surplus, which supports muscle gain if protein stays high enough."
    if calorie_balance == 0:
        return "Your intake and expenditure were roughly balanced today."
    return "Your intake and expenditure were not strongly aligned with your stated goal today."


def explanation_for_deficiency(name: str) -> str | None:
    explanations = {
        "fiber": "Low fiber intake can reduce satiety and make appetite control harder across the day.",
        "magnesium": "Low magnesium may affect recovery, muscle function, and day-to-day energy levels.",
        "protein": "Low protein makes recovery and lean-mass retention harder, especially around training.",
    }
    return explanations.get(name)


def suggestions_for_deficiencies(user: User, deficiencies: list[Deficiency]) -> list[str]:
    suggestions: list[str] = []
    suggestion_library = SUGGESTION_LIBRARY[user.diet_type]

    for deficiency in deficiencies:
        for suggestion in suggestion_library.get(deficiency.name, []):
            if suggestion not in suggestions:
                suggestions.append(suggestion)

    return suggestions


def build_insights(user: User, summary: NutritionSummary, deficiencies: list[Deficiency]) -> InsightPayload:
    day_summary = summary_for_balance(user, summary)

    why_it_matters = []
    suggestions = suggestions_for_deficiencies(user, deficiencies)

    if not deficiencies:
        why_it_matters.append("No major nutrient gaps were detected from the foods currently in the reference catalog.")
        suggestions.append("Keep repeating the meal structure that supported today’s intake and training demand.")
    else:
        for deficiency in deficiencies:
            explanation = explanation_for_deficiency(deficiency.name)
            if explanation and explanation not in why_it_matters:
                why_it_matters.append(explanation)

    if summary.foods_missing_from_catalog:
        why_it_matters.append(
            "Some foods were not in the nutrition reference catalog, so the totals may be slightly understated."
        )

    return InsightPayload(
        summary=day_summary,
        why_it_matters=why_it_matters[:3],
        suggestions=suggestions[:3],
        source="fallback-coach-v1",
    )


async def build_daily_analysis(session: AsyncSession, user_id: int, target_date: date) -> DailyAnalysisResponse:
    user = await get_user_or_404(session, user_id)
    food_logs = await list_food_logs(session, user_id, target_date)
    activity_logs = await list_activity_logs(session, user_id, target_date)
    summary = await summarize_day(
        session,
        user=user,
        food_logs=food_logs,
        activity_logs=activity_logs,
        target_date=target_date,
    )
    deficiencies = detect_deficiencies(summary, user)
    context = build_context(user, summary, deficiencies, activity_logs)
    # insights = build_insights(user, summary, deficiencies)
    insights = await generate_llm_insights(context, user, user_id, target_date)
    return DailyAnalysisResponse(
        user_id=user_id,
        context=context,
        nutrition_summary=summary,
        deficiencies=deficiencies,
        insights=insights,
    )