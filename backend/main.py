from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import ALLOWED_ORIGINS
from src.controller import api_router


app = FastAPI(title="Datalogger", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "Active"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # dev only
    )
