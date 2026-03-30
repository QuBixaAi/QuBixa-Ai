from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from db.sqlite_db import db_manager
from core.skill_loader import skill_loader
from core.training_manager import training_manager
from core.connection_manager import connection_manager
from utils.logger import logger_instance as logger

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    agent_name: str
    message: str
    use_rag: bool = False
    skill_context: str = None

class TrainingRequest(BaseModel):
    agent_name: str
    training_data: List[Dict[str, str]]

# Health check
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Qubixa AI"}

# Get all agents
@router.get("/agents")
async def get_agents():
    """Get list of all available agents"""
    try:
        agents = [
            {
                "name": "Analyzer Agent",
                "role": "Campaign Analyst",
                "status": "active"
            },
            {
                "name": "Keyword Agent",
                "role": "Keyword Optimizer",
                "status": "active"
            }
        ]
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get agent history
@router.get("/agents/{agent_name}/history")
async def get_agent_history(agent_name: str):
    """Get conversation history for a specific agent"""
    try:
        history = db_manager.get_agent_history(agent_name)
        return {
            "agent_name": agent_name,
            "history": [
                {
                    "input": h[0],
                    "output": h[1],
                    "timestamp": h[2]
                }
                for h in history
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get all skills
@router.get("/skills")
async def get_skills():
    """Get list of all available skills"""
    try:
        skills = skill_loader.get_all_skills()
        return {
            "total": len(skills),
            "skills": [
                {
                    "name": name,
                    "type": skill.get("type", "general"),
                    "has_instructions": bool(skill.get("instructions")),
                    "has_metadata": bool(skill.get("metadata"))
                }
                for name, skill in skills.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get specific skill
@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get details of a specific skill"""
    try:
        skill = skill_loader.get_skill(skill_name)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        return skill
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Train agent
@router.post("/agents/{agent_name}/train")
async def train_agent(agent_name: str, request: TrainingRequest):
    """Train an agent with new examples"""
    try:
        success = await training_manager.retrain_agent(
            agent_name,
            request.training_data
        )
        return {
            "success": success,
            "agent_name": agent_name,
            "examples_trained": len(request.training_data)
        }
    except Exception as e:
        logger.error(f"Error training agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get connection info
@router.get("/connections")
async def get_connections():
    """Get information about active WebSocket connections"""
    try:
        return connection_manager.get_connection_info()
    except Exception as e:
        logger.error(f"Error fetching connections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Scan skills
@router.post("/skills/scan")
async def scan_skills():
    """Trigger a rescan of the skills directory"""
    try:
        skills = skill_loader.scan_skills()
        return {
            "success": True,
            "skills_loaded": len(skills)
        }
    except Exception as e:
        logger.error(f"Error scanning skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Excel upload and analysis
from fastapi import UploadFile, File
import os

@router.post("/analyze/excel")
async def analyze_excel(file: UploadFile = File(...)):
    """Upload and analyze Excel file with data validation and DuckDB analytics"""
    try:
        # Save uploaded file
        upload_dir = "./data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate and load data
        from utils.excel_processor import excel_processor
        
        validation_result = excel_processor.validate_and_load(file_path)
        
        if not validation_result["success"]:
            return {
                "success": False,
                "error": validation_result.get("error"),
                "validation": validation_result.get("validation")
            }
        
        # Perform analysis using DuckDB
        analysis = excel_processor.analyze_keywords()
        predictions = excel_processor.generate_predictions(7)
        
        # Export to Parquet for efficient storage
        parquet_path = file_path.replace('.csv', '.parquet').replace('.xlsx', '.parquet')
        excel_processor.duckdb.export_to_parquet("keywords", parquet_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "validation": validation_result.get("validation"),
            "rows_analyzed": validation_result.get("rows_loaded"),
            "analysis": analysis,
            "predictions": predictions,
            "parquet_export": parquet_path
        }
    
    except Exception as e:
        logger.error(f"Error analyzing Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/campaign")
async def analyze_campaign_with_excel(
    campaign_data: Dict[str, Any],
    excel_file: str = None
):
    """Analyze campaign with optional Excel data"""
    try:
        from agents.analyzer_agent import analyzer_agent
        
        # This would need a client_id - for now return analysis structure
        return {
            "message": "Use WebSocket endpoint for real-time analysis",
            "websocket": "/api/ws/{client_id}",
            "message_format": {
                "type": "analyze_campaign",
                "campaign_data": campaign_data,
                "excel_file": excel_file
            }
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
