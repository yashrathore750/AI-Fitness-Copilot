from datetime import date, datetime

from pydantic import BaseModel, Field

from app.types import DietType, Goal


class UserCreate(BaseModel):
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    goal: Goal
    diet_type: DietType


class UserRead(UserCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FoodLogCreate(BaseModel):
    user_id: int
    food_name: str = Field(min_length=1, max_length=100)
    servings: float = Field(gt=0)
    logged_at: datetime | None = None


class FoodLogRead(FoodLogCreate):
    id: int
    logged_at: datetime

    model_config = {"from_attributes": True}


class ActivityLogCreate(BaseModel):
    user_id: int
    steps: int = Field(default=0, ge=0)
    workout_type: str | None = Field(default=None, max_length=100)
    duration_minutes: int = Field(default=0, ge=0)
    calories_burned_override: float | None = Field(default=None, ge=0)
    logged_at: datetime | None = None


class ActivityLogRead(ActivityLogCreate):
    id: int
    logged_at: datetime

    model_config = {"from_attributes": True}


class Deficiency(BaseModel):
    name: str
    actual: float
    target: float
    unit: str
    severity: str


class NutritionSummary(BaseModel):
    date: date
    calories_in: float
    calories_out: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    vitamins: dict[str, float]
    minerals: dict[str, float]
    steps: int
    workout_minutes: int
    foods_missing_from_catalog: list[str]


class InsightPayload(BaseModel):
    summary: str
    why_it_matters: list[str]
    suggestions: list[str]
    source: str


class AnalysisContext(BaseModel):
    user_goal: Goal
    diet_type: DietType
    activity: dict[str, object]
    nutrition_summary: NutritionSummary
    deficiencies: list[Deficiency]


class DailyAnalysisResponse(BaseModel):
    user_id: int
    context: AnalysisContext
    nutrition_summary: NutritionSummary
    deficiencies: list[Deficiency]
    insights: InsightPayload