"""FastAPI application for StoreOps API."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from storeops.activities import routes as activities_routes
from storeops.alerts import routes as alerts_routes
from storeops.programmes import routes as programmes_routes
from storeops.reports import routes as reports_routes
from storeops.staff import routes as staff_routes

app = FastAPI(title="StoreOps API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from all modules
app.include_router(activities_routes.router)
app.include_router(programmes_routes.router)
app.include_router(staff_routes.router)
app.include_router(alerts_routes.router)
app.include_router(reports_routes.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - API welcome message."""
    return {"status": "ok", "message": "StoreOps API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
