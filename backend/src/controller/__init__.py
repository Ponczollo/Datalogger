from fastapi import APIRouter

from src.controller.health import health_router
from src.controller.device import device_router
from src.controller.user import user_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(device_router)
api_router.include_router(user_router)
