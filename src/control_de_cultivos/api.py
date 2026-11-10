"""FastAPI backend for CAP Management System."""
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
import os
import httpx

# Initialize FastAPI app
app = FastAPI(
    title="CAP Management API",
    description="Backend for parcel and campaign management",
    version="1.0"
)

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8000))
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8001))
AZF_BASE_URL = os.getenv("AZURE_FUNCTIONS_BASE_URL", "http://127.0.0.1:7071/api")

# MARK: Root Endpoints
@app.get("/", tags=["Root"])
async def root():
    """API documentation page"""
    return JSONResponse(content={
        "message": "CAP Management System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "gui_streamlit_port": STREAMLIT_PORT,
        "api_port": FASTAPI_PORT
    })

@app.get("/health", tags=["Health"])
async def health_check():
    """Check API status"""
    return JSONResponse(content={"status": "healthy", "code": 200})


@app.get("/api/status", tags=["Info"])
async def get_status():
    """Get detailed API status and configuration"""
    return JSONResponse(content={
        "service": "CAP Management",
        "streamlit_port": STREAMLIT_PORT,
        "fastapi_port": FASTAPI_PORT,
        "azure_functions_available": True,
        "user_data_manager_path": "/src/user_data_manager"
    })

@app.get("/proxy/user_data/explotations", tags=["Proxy"])
async def user_explotations(
    user: str = Query(...),
    user_key: str = Query(..., alias="userKey"),
    check: int = Query(0),
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AZF_BASE_URL}/get_explotations_list",
            params={
                "check": check,
                "user": user,
                "userKey": user_key,
            },
        )
        response.raise_for_status()
        return response.json()


@app.get("/proxy/user_data/explotation", tags=["Proxy"])
async def user_explotation(
    user: str = Query(...),
    user_key: str = Query(..., alias="userKey"),
    explotation: str = Query(...),
    check: int = Query(0),
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AZF_BASE_URL}/get_explotation_data",
            params={
                "check": check,
                "user": user,
                "userKey": user_key,
                "explotation": explotation,
            },
        )
        response.raise_for_status()
        return response.json()



if __name__ == "__main__":
    # This runs when the module is executed directly
    uvicorn.run(
        app,  # Import path to the app
        host="127.0.0.1",   # Bind to localhost
        port=8001,          # API port
        reload=True         # Reload on code changes (development mode)
    )