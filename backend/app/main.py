from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, Base
from app import models  # noqa: ensure models registered

# Auto-create tables (Alembic still preferred for production Postgres)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory & Order Management API",
    version="1.0.0",
    description="Secure full-stack inventory and order management backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Inventory & Order Management API", "docs": "/docs", "health": "/health"}
