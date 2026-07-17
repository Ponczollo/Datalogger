from fastapi import APIRouter

from src.controller.health import health_router

api_router = APIRouter()
api_router.include_router(health_router)
