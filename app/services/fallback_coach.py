"""Fallback local coach for generating insights when LLM is unavailable."""

from app.catalog import SUGGESTION_LIBRARY
from app.models import User
from app.schemas import Deficiency, InsightPayload, NutritionSummary
from app.types import Goal


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
    """Generate insights using the fallback local coach."""
    day_summary = summary_for_balance(user, summary)

    why_it_matters = []
    suggestions = suggestions_for_deficiencies(user, deficiencies)

    if not deficiencies:
        why_it_matters.append("No major nutrient gaps were detected from the foods currently in the reference catalog.")
        suggestions.append("Keep repeating the meal structure that supported today's intake and training demand.")
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
