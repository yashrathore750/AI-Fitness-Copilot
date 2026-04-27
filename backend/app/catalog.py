from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NutritionReference
from app.types import DietType

DEFAULT_NUTRITION_ENTRIES: Sequence[dict[str, object]] = (
    {
        "food_name": "oats",
        "serving_description": "40 g dry oats",
        "calories": 156.0,
        "protein_g": 6.8,
        "carbs_g": 26.5,
        "fat_g": 3.1,
        "fiber_g": 4.1,
        "vitamins": {"b1": 0.3},
        "minerals": {"magnesium": 54.0, "iron": 1.7},
    },
    {
        "food_name": "spinach",
        "serving_description": "100 g cooked spinach",
        "calories": 23.0,
        "protein_g": 2.9,
        "carbs_g": 3.6,
        "fat_g": 0.4,
        "fiber_g": 2.4,
        "vitamins": {"vitamin_k": 0.48, "folate": 0.19},
        "minerals": {"magnesium": 79.0, "iron": 2.7},
    },
    {
        "food_name": "lentils",
        "serving_description": "150 g cooked lentils",
        "calories": 174.0,
        "protein_g": 13.5,
        "carbs_g": 30.0,
        "fat_g": 0.8,
        "fiber_g": 11.9,
        "vitamins": {"folate": 0.27},
        "minerals": {"magnesium": 54.0, "iron": 3.3},
    },
    {
        "food_name": "pumpkin seeds",
        "serving_description": "30 g pumpkin seeds",
        "calories": 170.0,
        "protein_g": 8.5,
        "carbs_g": 4.0,
        "fat_g": 14.0,
        "fiber_g": 1.7,
        "vitamins": {"vitamin_e": 0.6},
        "minerals": {"magnesium": 156.0, "zinc": 2.2},
    },
    {
        "food_name": "banana",
        "serving_description": "1 medium banana",
        "calories": 105.0,
        "protein_g": 1.3,
        "carbs_g": 27.0,
        "fat_g": 0.3,
        "fiber_g": 3.1,
        "vitamins": {"vitamin_b6": 0.4, "vitamin_c": 8.7},
        "minerals": {"magnesium": 32.0, "potassium": 422.0},
    },
    {
        "food_name": "paneer",
        "serving_description": "100 g paneer",
        "calories": 265.0,
        "protein_g": 18.0,
        "carbs_g": 3.4,
        "fat_g": 20.8,
        "fiber_g": 0.0,
        "vitamins": {"vitamin_b12": 0.8},
        "minerals": {"calcium": 208.0, "magnesium": 16.0},
    },
    {
        "food_name": "egg",
        "serving_description": "1 large egg",
        "calories": 72.0,
        "protein_g": 6.3,
        "carbs_g": 0.4,
        "fat_g": 4.8,
        "fiber_g": 0.0,
        "vitamins": {"vitamin_b12": 0.5, "vitamin_d": 1.1},
        "minerals": {"selenium": 15.4, "magnesium": 6.0},
    },
    {
        "food_name": "chicken breast",
        "serving_description": "100 g cooked chicken breast",
        "calories": 165.0,
        "protein_g": 31.0,
        "carbs_g": 0.0,
        "fat_g": 3.6,
        "fiber_g": 0.0,
        "vitamins": {"vitamin_b6": 0.6, "niacin": 13.7},
        "minerals": {"magnesium": 29.0, "selenium": 27.6},
    },
)

WORKOUT_MET_VALUES = {
    "leg_day": 6.0,
    "push_day": 5.5,
    "pull_day": 5.5,
    "run": 9.8,
    "cycling": 7.5,
    "yoga": 3.0,
}

SUGGESTION_LIBRARY: dict[DietType, dict[str, list[str]]] = {
    DietType.VEG: {
        "fiber": [
            "Add a lentil bowl or chana salad to your next meal.",
            "Swap one snack for oats with fruit and chia seeds.",
            "Include a larger vegetable portion at dinner, especially spinach or beans.",
        ],
        "magnesium": [
            "Add pumpkin seeds or roasted seeds to curd, oats, or salad.",
            "Use spinach or leafy greens in dal, paratha filling, or curry.",
            "Include lentils or mixed legumes in one more meal today.",
        ],
        "protein": [
            "Add paneer, Greek yogurt, or soy to your next meal for a dense protein bump.",
            "Build one meal around lentils plus dairy instead of relying on carbs alone.",
            "Use a protein-rich snack such as curd with seeds between meals.",
        ],
    },
    DietType.EGGETARIAN: {
        "fiber": [
            "Add fruit with oats or curd instead of a lower-fiber snack.",
            "Increase legumes or vegetables in one main meal.",
            "Pair eggs with spinach, mushrooms, or beans instead of refined carbs alone.",
        ],
        "magnesium": [
            "Add pumpkin seeds or spinach to your egg-based meals.",
            "Use lentils or beans in one extra meal to improve magnesium coverage.",
            "Choose banana plus seeds as a recovery snack.",
        ],
        "protein": [
            "Add 2 eggs or Greek yogurt to the meal with the least protein.",
            "Anchor one meal around eggs plus lentils for a more complete protein profile.",
            "Use cottage cheese or curd as a recovery snack after training.",
        ],
    },
    DietType.NON_VEG: {
        "fiber": [
            "Keep the protein source, but add legumes or a larger vegetable serving.",
            "Use oats or fruit for one snack instead of another low-fiber option.",
            "Include salad or cooked greens with your next main meal.",
        ],
        "magnesium": [
            "Add pumpkin seeds, spinach, or beans alongside your protein source.",
            "Choose banana plus seeds as a simple recovery snack.",
            "Use lentils or greens in the next meal to close the magnesium gap.",
        ],
        "protein": [
            "Increase the lean protein portion in the meal closest to training.",
            "Use chicken, eggs, or yogurt in one more feeding window today.",
            "Spread protein across meals instead of loading most of it into dinner.",
        ],
    },
    DietType.VEGAN: {
        "fiber": [
            "Add beans, lentils, or oats to the next meal for an efficient fiber increase.",
            "Choose fruit with seeds or nuts as your next snack.",
            "Double the vegetable portion in one main meal.",
        ],
        "magnesium": [
            "Use pumpkin seeds or mixed seeds on top of oats, salads, or cooked vegetables.",
            "Include spinach or other leafy greens in your next meal.",
            "Add lentils or beans to improve both magnesium and protein together.",
        ],
        "protein": [
            "Add tofu, tempeh, or soy yogurt to the next meal.",
            "Pair legumes with grains to improve total protein quality.",
            "Use a higher-protein snack instead of fruit alone when recovering from training.",
        ],
    },
}


async def seed_reference_data(session: AsyncSession) -> None:
    existing_rows = await session.scalars(select(NutritionReference.food_name))
    existing = set(existing_rows.all())

    for entry in DEFAULT_NUTRITION_ENTRIES:
        food_name = str(entry["food_name"])
        if food_name in existing:
            continue
        session.add(NutritionReference(**entry))

    await session.commit()