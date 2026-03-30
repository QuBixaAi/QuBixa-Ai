from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.connection_manager import connection_manager
from core.agent_runner import agent_runner
from agents.analyzer_agent import analyzer_agent
from agents.keyword_agent import keyword_agent
from utils.logger import logger_instance as logger
import json
import uuid

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Main WebSocket endpoint for real-time agent communication.
    Handles chat messages and streams responses.
    """
    logger.info(f"New WebSocket connection attempt from client: {client_id}")
    await connection_manager.connect(websocket, client_id)
    logger.info(f"Client {client_id} connected successfully")
    
    try:
        # Send welcome message
        await connection_manager.send_to_client({
            "type": "system",
            "content": "Connected to Qubixa AI. Ready to assist!",
            "timestamp": str(uuid.uuid4())
        }, client_id)
        
        logger.info(f"Welcome message sent to {client_id}")
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received data from {client_id}: {data[:100]}")
            
            message_data = json.loads(data)
            
            # Extract message details
            message_type = message_data.get("type", "chat")
            content = message_data.get("content", "")
            agent_name = message_data.get("agent", "Analyzer Agent")
            skill_context = message_data.get("skill_context")
            use_rag = message_data.get("use_rag", False)
            
            logger.info(f"Processing message - Type: {message_type}, Agent: {agent_name}, Content: {content[:50]}")
            
            # Log received message
            await connection_manager.send_log(
                f"Received: {content[:50]}...",
                client_id,
                "info"
            )
            
            # Handle different message types
            if message_type == "chat":
                logger.info(f"Starting agent execution for {agent_name}")
                
                # Run agent and stream response
                response = await agent_runner.run_agent(
                    agent_name=agent_name,
                    user_input=content,
                    client_id=client_id,
                    skill_context=skill_context,
                    use_rag=use_rag,
                    stream=True
                )
                
                logger.info(f"Agent execution complete. Response length: {len(response)}")
                
                # Send completion message
                await connection_manager.send_to_client({
                    "type": "complete",
                    "content": "Response complete",
                    "full_response": response
                }, client_id)
            
            elif message_type == "analyze_campaign":
                logger.info("Handling campaign analysis")
                # Handle campaign analysis
                campaign_data = message_data.get("campaign_data", {})
                response = await analyzer_agent.analyze_campaign(
                    campaign_data,
                    client_id
                )
                
                await connection_manager.send_to_client({
                    "type": "complete",
                    "content": response
                }, client_id)
            
            elif message_type == "optimize_keywords":
                logger.info("Handling keyword optimization")
                # Handle keyword optimization
                keywords = message_data.get("keywords", [])
                context = message_data.get("context", "")
                response = await keyword_agent.optimize_keywords(
                    keywords,
                    context,
                    client_id
                )
                
                await connection_manager.send_to_client({
                    "type": "complete",
                    "content": response
                }, client_id)
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, client_id)
        logger.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        logger.exception(e)
        connection_manager.disconnect(websocket, client_id)

@router.websocket("/ws/logs/{client_id}")
async def logs_websocket(websocket: WebSocket, client_id: str):
    """
    Dedicated WebSocket endpoint for streaming logs.
    """
    log_client_id = f"logs_{client_id}"
    await connection_manager.connect(websocket, log_client_id)
    
    try:
        await connection_manager.send_to_client({
            "type": "system",
            "content": "Log stream connected"
        }, log_client_id)
        
        # Keep connection alive and stream logs
        while True:
            # Wait for messages (logs will be pushed from other parts of the system)
            data = await websocket.receive_text()
            # Echo back for keepalive
            await websocket.send_text(json.dumps({"type": "ping", "content": "pong"}))
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, log_client_id)
        logger.info(f"Log client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"Log WebSocket error: {str(e)}")
        connection_manager.disconnect(websocket, log_client_id)
