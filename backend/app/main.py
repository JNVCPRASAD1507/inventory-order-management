from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, Base
from app import models
from app.api.v1 import users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory & Order Management",
    version="1.0.0",
    description="Secure full-stack inventory and order management.",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://localhost:5173",
    #     "http://10.138.134.207:5173",
    # ],
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(api_router, prefix="/api/v1")
# app.include_router(users.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "Inventory & Order Management API",
        "docs": "/docs",
        "health": "/health",
    }
