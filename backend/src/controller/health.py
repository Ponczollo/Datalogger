from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
def healthcheck():
    return {"status": "OK"}
