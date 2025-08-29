"""
Main FastAPI application for GoWombat Doodles Generator.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import time
from typing import Dict, Any

from .config import get_settings
from .models import DoodleRequest, DoodleResponse, HealthResponse
from .services.gemini_service import GeminiService


settings = get_settings()
rate_limit_storage: Dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    """
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    print("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_rate_limit(client_ip: str) -> bool:
    """
    Check if client has exceeded rate limit.
    
    Args:
        client_ip: Client IP address
        
    Returns:
        bool: True if within limits, False if exceeded
    """
    current_time = time.time()
    
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < settings.rate_limit_period
    ]
    
    if len(rate_limit_storage[client_ip]) >= settings.rate_limit_requests:
        return False
    
    rate_limit_storage[client_ip].append(current_time)
    return True


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the main HTML page.
    """
    html_path = Path("/frontend/templates/index.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>GoWombat Doodles Generator</h1>
                <p>Frontend is not configured. Please use the API endpoints directly.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@app.post("/api/generate-doodle", response_model=DoodleResponse)
async def generate_doodle(request: Request, doodle_request: DoodleRequest):
    """
    Generate a GoWombat doodle for the specified occasion.
    
    Args:
        request: FastAPI request object
        doodle_request: Doodle generation request
        
    Returns:
        DoodleResponse: Generated doodle information
    """
    
    client_ip = request.client.host if request.client else "unknown"
    
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per hour."
        )
    
    try:
        async with GeminiService() as service:
            result = await service.generate_doodle(
                occasion=doodle_request.occasion,
                style_hint=doodle_request.style_hint
            )
            
            if result["success"]:
                return DoodleResponse(
                    success=True,
                    image_url=result.get("image_url"),
                    image_base64=result.get("image_base64"),
                    occasion=doodle_request.occasion,
                    generation_time=result["generation_time"]
                )
            else:
                return DoodleResponse(
                    success=False,
                    occasion=doodle_request.occasion,
                    generation_time=result["generation_time"],
                    error=result.get("error", "Unknown error occurred")
                )
                
    except Exception as e:
        return DoodleResponse(
            success=False,
            occasion=doodle_request.occasion,
            generation_time=0,
            error=f"Server error: {str(e)}"
        )


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """
    Serve static files.
    """
    static_path = Path("/frontend/static") / file_path
    if static_path.exists() and static_path.is_file():
        return FileResponse(static_path)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )