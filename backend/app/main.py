"""FastAPI Application Entrypoint

Main application setup, middleware configuration, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Campus marketplace platform connecting verified students with local businesses",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
)

# CORS Middleware
# Allow requests from mobile app and admin panel origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Trusted Host Middleware (only in production)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["aaspaas.com", "*.aaspaas.com", "api.aaspaas.com"],
    )


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add defense-in-depth security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers[
        "Permissions-Policy"
    ] = "geolocation=(self), camera=(), microphone=()"
    response.headers[
        "Content-Security-Policy"
    ] = "default-src 'self'; frame-ancestors 'none';"

    if settings.is_production:
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"

    return response


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning basic API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else None,
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers.

    Returns basic health status. In production, this should also check:
    - Database connectivity
    - External service availability
    - Disk space
    - Memory usage
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }


# API v1 health check
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Health"])
async def api_health_check():
    """API v1 health check endpoint."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "api_version": "v1",
            "environment": settings.ENVIRONMENT,
        },
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found",
            },
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 Internal Server Error."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "An internal server error occurred",
            },
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"API documentation: {'Enabled' if settings.DEBUG else 'Disabled'}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    print(f"Shutting down {settings.PROJECT_NAME}")


# Include routers
from app.api.v1.endpoints import (
    admin,
    auth,
    businesses,
    campuses,
    categories,
    maps,
    notifications,
    offers,
    owner,
    reviews,
    services,
    students,
)

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(
    admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"]
)
app.include_router(
    owner.router, prefix=f"{settings.API_V1_PREFIX}/owner", tags=["owner"]
)
app.include_router(
    notifications.router,
    prefix=f"{settings.API_V1_PREFIX}/notifications",
    tags=["notifications"],
)
app.include_router(
    students.router, prefix=f"{settings.API_V1_PREFIX}/students", tags=["students"]
)
app.include_router(
    businesses.router,
    prefix=f"{settings.API_V1_PREFIX}/businesses",
    tags=["businesses"],
)
app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_PREFIX}/categories",
    tags=["categories"],
)
app.include_router(
    services.router, prefix=f"{settings.API_V1_PREFIX}/services", tags=["services"]
)
app.include_router(
    reviews.router, prefix=f"{settings.API_V1_PREFIX}/reviews", tags=["reviews"]
)
app.include_router(
    offers.router, prefix=f"{settings.API_V1_PREFIX}/offers", tags=["offers"]
)
app.include_router(
    campuses.router,
    prefix=f"{settings.API_V1_PREFIX}/campuses",
    tags=["campuses"],
)
app.include_router(maps.router, prefix=f"{settings.API_V1_PREFIX}/map", tags=["map"])

# TODO: Include other routers in future phases
# from app.api.v1.endpoints import users, colleges, campuses
# app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
# app.include_router(colleges.router, prefix=settings.API_V1_PREFIX, tags=["colleges"])
# app.include_router(campuses.router, prefix=settings.API_V1_PREFIX, tags=["campuses"])
