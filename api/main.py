"""
FastAPI Application Entrypoint

This module bootstraps the FastAPI backend, configuring middleware,
CORS policies, and routing across all specific domain modules (funds, aum, reports, etc.).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.middleware import RequestLoggingMiddleware
from api.routers import funds, categories, compare, pipeline, reports, aum, auth, portfolios, dashboard
from config.logging_config import get_logger

logger = get_logger("api.main")

app = FastAPI(
    title="AMFI Mutual Fund Data Intelligence Platform API",
    description="Production-grade analytics backend for Indian Mutual Fund daily NAVs, performance, and SIP simulation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js frontend or any external callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable Custom Latency & Error Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Register Module Routers
app.include_router(funds.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(aum.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(portfolios.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.get("/health", tags=["Health Checks"])
async def health_check():
    """
    Verifies that the backend API is up and running.
    """
    return {"status": "healthy", "service": "AMFI Intelligence Platform Backend"}
