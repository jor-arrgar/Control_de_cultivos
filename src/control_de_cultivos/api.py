"""FastAPI backend for CAP Management System."""
import os
import traceback

import httpx
import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import json

DEBUG_MODE = os.getenv("FASTAPI_DEBUG", "true").lower() in {"1", "true", "yes", "on"}

# Initialize FastAPI app
app = FastAPI(
    title="CAP Management API",
    description="Backend for parcel and campaign management",
    version="1.0",
    debug=DEBUG_MODE,
)

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8000))
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8001))
AZF_BASE_URL = os.getenv("AZURE_FUNCTIONS_BASE_URL", "http://127.0.0.1:7071/api")


# MARK: Exception Handlers
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "message": "HTTP error",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if DEBUG_MODE else "An unexpected server error occurred",
            "path": str(request.url.path),
            "error_type": type(exc).__name__,
        },
    )


# MARK: Root Endpoints
@app.get("/", tags=["Root"])
async def root():
    return JSONResponse(
        content={
            "message": "CAP Management System API",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "gui_streamlit_port": STREAMLIT_PORT,
            "api_port": FASTAPI_PORT,
        }
    )

# MARK: Health Checks
@app.get("/health", tags=["Health"])
async def health_check(
    level: int = Query(1, description="Health check level (0-1)"),
):
    if level == 0:
        return JSONResponse(content={"status": "healthy", "code": 200})

    elif level == 1:
        # Check Azure Functions availability
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{AZF_BASE_URL}/health")
                response.raise_for_status()
                azf_status = response.json()
        except Exception as e:
            azf_status = {"status": "unhealthy", "error": str(e)}

        return JSONResponse(
            content={
                "proxy_status": "healthy" if azf_status.get("status") == "healthy" else "unhealthy",
                "azure_functions_status": azf_status,
            }
        )


@app.get("/api/status", tags=["Info"])
async def get_status():
    return JSONResponse(
        content={
            "service": "CAP Management",
            "streamlit_port": STREAMLIT_PORT,
            "fastapi_port": FASTAPI_PORT,
            "azure_functions_available": True,
            "user_data_manager_path": "/src/user_data_manager",
        }
    )


# MARK: General database endpoints
@app.get("/proxy/generaldb/get_table_struct", tags=["Proxy"])
async def get_table_struct(
    table_name: str = Query(...),
):

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AZF_BASE_URL}/get_table_structure",
            params={
                "table_name": table_name,
                "check":0
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()

@app.get("/proxy/generaldb/get_column_uniques", tags=["Proxy"])
async def get_column_uniques(
    table_name: str = Query(...),
    column_name: str = Query(...)
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AZF_BASE_URL}/get_column_uniques",
            params={
                "table_name":table_name,
                "column_name":column_name,
                "check":0
            }
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()
    



# MARK: User data Endpoints
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
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
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
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()


@app.get("/proxy/user_data/user_info", tags=["Proxy"])
async def user_info(user: str = Query(...)):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AZF_BASE_URL}/get_user_data",
            params={"user": user, "check": 0},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        return response.json()


@app.post("/proxy/user_data/insert_new_user", tags=["Proxy"])
async def new_user(user_data: dict = Body(..., description="User data in JSON format")):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AZF_BASE_URL}/insert_new_user",
            json=user_data,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        try:
            return response.json()
        except json.JSONDecodeError:
            return response






if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=True,
    )