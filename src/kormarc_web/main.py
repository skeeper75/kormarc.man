# TAG:SPEC-WEB-001:INIT
# TAG:SPEC-WEB-001:API:RECORDS
# TAG:SPEC-WEB-001:API:SEARCH
"""
FastAPI main application for KORMARC Web API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kormarc_web.api.routes import records, search

# Create FastAPI application
app = FastAPI(
    title="KORMARC Web API",
    description="Read-only API for KORMARC record browsing and search",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(records.router)
app.include_router(search.router)


@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "name": "KORMARC Web API",
        "version": "1.0.0",
        "description": "Read-only API for KORMARC record browsing and search",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
