from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api import routes, websocket
from core.skill_loader import skill_loader
from utils.logger import logger_instance as logger
import uvicorn
import os

# Load environment variables first
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Qubixa AI - Agentic Ad Optimization Platform",
    description="Real-time AI Agent System with WebSocket streaming",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api", tags=["API"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 60)
    logger.info("Starting Qubixa AI Platform...")
    logger.info("=" * 60)
    
    # Verify API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ CRITICAL: OPENROUTER_API_KEY not found in environment!")
        logger.error("Please check your .env file")
    else:
        logger.info(f"✅ OpenRouter API Key loaded: {api_key[:20]}...")
    
    # Verify model
    model = os.getenv("DEFAULT_MODEL")
    logger.info(f"✅ Default Model: {model}")
    
    # Load skills
    try:
        skills = skill_loader.scan_skills()
        logger.info(f"✅ Loaded {len(skills)} skills")
    except Exception as e:
        logger.error(f"❌ Error loading skills: {e}")
    
    # Initialize database
    try:
        from db.sqlite_db import db_manager
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    
    logger.info("=" * 60)
    logger.info("✅ Qubixa AI Platform started successfully!")
    logger.info("📊 Dashboard: http://localhost:3000")
    logger.info("📚 API Docs: http://localhost:8000/docs")
    logger.info("🔌 WebSocket: ws://localhost:8000/api/ws/{client_id}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Qubixa AI Platform...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Qubixa AI Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/api/ws/{client_id}"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
