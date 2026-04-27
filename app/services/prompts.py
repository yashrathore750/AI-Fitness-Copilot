from app.schemas import AnalysisContext


def build_insight_prompt(context: AnalysisContext) -> tuple[str, str]:
    """Build system and user prompts from analysis context."""
    system = """You are a nutrition coach for fitness. Provide concise, actionable insights.

Respond in JSON format only, with this structure:
{
    "summary": "one-line summary of the day's nutrition and activity",
    "why_it_matters": ["reason1", "reason2", "reason3"],
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
}

Keep suggestions specific and diet-appropriate."""

    deficiencies_text = "\n".join(
        [
            f"- {d.name}: {d.actual}{d.unit} (target: {d.target}{d.unit}, severity: {d.severity})"
            for d in context.deficiencies
        ]
    )

    user = f"""
User Profile:
- Goal: {context.user_goal.value}
- Diet Type: {context.diet_type.value}

Today's Nutrition:
- Calories In: {context.nutrition_summary.calories_in}
- Calories Out: {context.nutrition_summary.calories_out}
- Protein: {context.nutrition_summary.protein_g}g
- Carbs: {context.nutrition_summary.carbs_g}g
- Fat: {context.nutrition_summary.fat_g}g
- Fiber: {context.nutrition_summary.fiber_g}g

Activity:
- Steps: {context.activity.get("steps", 0)}
- Workout Minutes: {context.activity.get("workout_minutes", 0)}
- Workouts: {", ".join(context.activity.get("workouts", []))}

Deficiencies Detected:
{deficiencies_text if deficiencies_text else "None detected"}

Provide:
1. A summary of their day aligned with their goal
2. Why any deficiencies matter for their specific goal and diet
3. 2-3 specific, actionable food suggestions for their diet type
"""

    return system, user