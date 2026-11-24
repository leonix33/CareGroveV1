from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.routers import admin, auth, care, directory, family, provider, public
from app.seed import seed

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="CareGrove API", version="0.1.0", lifespan=lifespan)

if settings.environment == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.public_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(directory.router, prefix="/api")
app.include_router(care.router, prefix="/api")
app.include_router(provider.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(public.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "caregrove-api", "env": settings.environment}
