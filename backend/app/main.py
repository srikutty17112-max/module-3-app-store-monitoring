from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models_app  # Import to ensure tables are created
from app.routers import brands, apps, scans, detection

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Module 3: App Store Monitoring & Suspicious App Detection",
    description="Digital Risk Protection Platform - Module 3",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])
app.include_router(detection.router, prefix="/api/detection", tags=["detection"])

@app.get("/")
async def root():
    return {"message": "Module 3: App Store Monitoring & Suspicious App Detection API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "module": "3", "service": "app_store_monitoring"}