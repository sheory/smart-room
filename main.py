from fastapi import FastAPI
from app.config.settings import settings
from app.schemas.health_check import HealthCheck
from app.api.auth import auth_router
from app.api.rooms import room_router
from app.api.reservations import reservation_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

app.get("/health", response_model=HealthCheck, tags=["status"])
async def health_check():
    return HealthCheck(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION
    )


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(room_router, prefix="/rooms", tags=["Rooms"])
app.include_router(reservation_router, prefix="/reservations", tags=["Reservations"])