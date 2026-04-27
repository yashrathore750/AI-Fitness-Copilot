from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog import seed_reference_data
from app.core.config import get_settings
from app.db import Database, get_session
from app.models import ActivityLog, FoodLog, User
from app.schemas import ActivityLogCreate, ActivityLogRead, DailyAnalysisResponse, FoodLogCreate, FoodLogRead, UserCreate, UserRead
from app.services.analysis import build_daily_analysis, get_user_or_404, list_activity_logs, list_food_logs, normalize_food_name

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TargetDateDep = Annotated[date | None, Query()]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_app(database_url: str | None = None) -> FastAPI:
    settings = get_settings()
    database = Database(database_url or settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.database = database
        await database.init_models()
        async with database.session_factory() as session:
            await seed_reference_data(session)
        yield
        await database.dispose()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    @app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    async def create_user(payload: UserCreate, session: SessionDep) -> User:
        user = User(**payload.model_dump())
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @app.get("/users/{user_id}", response_model=UserRead)
    async def read_user(user_id: int, session: SessionDep) -> User:
        return await get_user_or_404(session, user_id)

    @app.post("/food-log", response_model=FoodLogRead, status_code=status.HTTP_201_CREATED)
    async def create_food_log(payload: FoodLogCreate, session: SessionDep) -> FoodLog:
        await get_user_or_404(session, payload.user_id)
        food_log = FoodLog(
            user_id=payload.user_id,
            food_name=normalize_food_name(payload.food_name),
            servings=payload.servings,
            logged_at=payload.logged_at or utc_now(),
        )
        session.add(food_log)
        await session.commit()
        await session.refresh(food_log)
        return food_log

    @app.get("/food-log", response_model=list[FoodLogRead])
    async def read_food_logs(
        user_id: int,
        target_date: TargetDateDep = None,
        session: SessionDep = None,
    ) -> list[FoodLog]:
        await get_user_or_404(session, user_id)
        return await list_food_logs(session, user_id, target_date or date.today())

    @app.post("/activity", response_model=ActivityLogRead, status_code=status.HTTP_201_CREATED)
    async def create_activity_log(
        payload: ActivityLogCreate,
        session: SessionDep,
    ) -> ActivityLog:
        await get_user_or_404(session, payload.user_id)
        activity_log = ActivityLog(
            **payload.model_dump(exclude={"logged_at"}),
            logged_at=payload.logged_at or utc_now(),
        )
        session.add(activity_log)
        await session.commit()
        await session.refresh(activity_log)
        return activity_log

    @app.get("/activity", response_model=list[ActivityLogRead])
    async def read_activity_logs(
        user_id: int,
        target_date: TargetDateDep = None,
        session: SessionDep = None,
    ) -> list[ActivityLog]:
        await get_user_or_404(session, user_id)
        return await list_activity_logs(session, user_id, target_date or date.today())

    @app.get("/analysis/today")
    async def analyze_today(
        user_id: int,
        target_date: TargetDateDep = None,
        session: SessionDep = None,
    ) -> DailyAnalysisResponse:
        return await build_daily_analysis(session, user_id, target_date or date.today())

    return app


app = create_app()