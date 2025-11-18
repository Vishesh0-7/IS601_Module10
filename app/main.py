"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler - initialize DB on startup.
    """
    from app.database import init_db
    init_db()
    yield


app = FastAPI(
    title="User Management API",
    description="FastAPI application with user registration and authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
from app.routes import router as user_router
app.include_router(user_router)


@app.get("/")
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to User Management API"}


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
