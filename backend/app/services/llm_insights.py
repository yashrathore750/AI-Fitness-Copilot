import json
import logging
from datetime import date

from openai import AsyncOpenAI, APIError

from app.core.config import get_settings
from app.models import User
from app.schemas import AnalysisContext, InsightPayload
from app.services.fallback_coach import build_insights

logger = logging.getLogger(__name__)


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


async def generate_llm_insights(context: AnalysisContext, user: User, user_id: int, target_date: date) -> InsightPayload:
    """Generate insights using OpenAI LLM with fallback to local coach."""
    settings = get_settings()

    # Fallback if no API key
    if not settings.openai_api_key:
        logger.info(f"No OpenAI API key configured; using fallback insights for user {user_id}")
        return build_insights(user, context.nutrition_summary, context.deficiencies)

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        system_prompt, user_prompt = build_insight_prompt(context)

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        response_text = response.choices[0].message.content
        logger.debug(f"LLM response for user {user_id}: {response_text}")

        # Parse JSON response
        parsed = json.loads(response_text)

        return InsightPayload(
            summary=parsed.get("summary", "No summary available"),
            why_it_matters=parsed.get("why_it_matters", []),
            suggestions=parsed.get("suggestions", []),
            source="openai-gpt",
        )

    except APIError as e:
        logger.error(f"OpenAI API error for user {user_id}: {e}")
        return build_insights(user, context.nutrition_summary, context.deficiencies)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response for user {user_id}: {e}")
        return build_insights(user, context.nutrition_summary, context.deficiencies)
    except Exception as e:
        logger.error(f"Unexpected error generating LLM insights for user {user_id}: {e}")
        return build_insights(user, context.nutrition_summary, context.deficiencies)