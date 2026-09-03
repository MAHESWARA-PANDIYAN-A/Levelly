"""
LEVELLY Backend — FastAPI Application Factory
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print(f"[START] LEVELLY Backend starting - environment: {settings.APP_ENV}")
    try:
        from app import models  # noqa
        Base.metadata.create_all(bind=engine)
        from app.models.user import User
        from app.core.database import SessionLocal
        from app.seed import seed_database
        with SessionLocal() as db:
            if db.query(User).count() == 0:
                print("[SEED] No users found. Auto-seeding initial database...")
                seed_database()
    except Exception as e:
        print(f"[WARN] Database startup check: {e}")
    yield
    # Shutdown
    print("[STOP] LEVELLY Backend shutting down")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="LEVELLY API",
        description="Financial resilience platform for gig and informal workers",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "healthy", "service": "LEVELLY API", "version": "1.0.0"}

    # Include API router
    app.include_router(api_router, prefix="/api")

    # Static frontend mounting (Serves React UI on the same URL)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(backend_dir, "static")
    if not os.path.exists(static_dir) or not os.path.exists(os.path.join(static_dir, "index.html")):
        # Fallback to frontend/dist if static is not directly inside backend
        static_dir = os.path.join(os.path.dirname(backend_dir), "frontend", "dist")

    if os.path.exists(static_dir) and os.path.exists(os.path.join(static_dir, "index.html")):
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.exists(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/")
        async def serve_root():
            return FileResponse(os.path.join(static_dir, "index.html"))

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
            file_path = os.path.join(static_dir, full_path)
            if full_path and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(static_dir, "index.html"))
    else:
        @app.get("/", tags=["System"])
        async def root():
            return {
                "status": "online",
                "service": "LEVELLY API",
                "docs": "/api/docs",
                "health": "/health",
            }

    return app


app = create_application()
