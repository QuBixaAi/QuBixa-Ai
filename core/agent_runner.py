import asyncio
from typing import Dict, List, Any, Optional
from services.openrouter_service import openrouter_service
from services.gemini_service import gemini_service
from core.connection_manager import connection_manager
from core.skill_loader import skill_loader
from knowbase.rag_system import rag_system
from db.sqlite_db import db_manager
from utils.logger import logger_instance as logger
import httpx
import json

class AgentRunner:
    """
    Core agent execution engine.
    Builds prompts, calls LLMs, and streams responses in real-time.
    """
    def __init__(self):
        self.openrouter = openrouter_service
        self.gemini = gemini_service
        self.skill_loader = skill_loader
        self.rag = rag_system
        self.connection_manager = connection_manager

    async def run_agent(
        self,
        agent_name: str,
        user_input: str,
        client_id: str,
        skill_context: Optional[str] = None,
        use_rag: bool = False,
        stream: bool = True
    ) -> str:
        """
        Execute an agent with given input.
        """
        try:
            logger.info(f"🚀 Agent runner starting for {agent_name} with input: {user_input}")
            
            # Log agent start
            await self.connection_manager.send_log(
                f"Starting agent: {agent_name}",
                client_id,
                "info"
            )

            # Simple system prompt
            system_prompt = self._get_agent_system_prompt(agent_name)
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            logger.info(f"📝 Calling OpenRouter with messages")

            # Use proper streaming
            if stream:
                response = await self._stream_response(messages, client_id)
            else:
                response = await self.openrouter.get_chat_completion(messages, stream=False)

            # Save to database
            db_manager.save_chat_message(agent_name, "user", user_input)
            db_manager.save_chat_message(agent_name, "assistant", response)

            await self.connection_manager.send_log(
                f"Agent {agent_name} completed",
                client_id,
                "success"
            )

            logger.info(f"🎉 Agent execution complete. Response length: {len(response)}")
            return response or "No response received"

        except Exception as e:
            error_msg = f"Error running agent {agent_name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.exception(e)
            await self.connection_manager.send_log(error_msg, client_id, "error")
            return f"Error: {str(e)}"

    async def _build_prompt(
        self,
        agent_name: str,
        user_input: str,
        skill_context: Optional[str],
        use_rag: bool
    ) -> str:
        """Build the complete prompt with context"""
        prompt_parts = []

        # Add skill context if provided
        if skill_context:
            skill = self.skill_loader.get_skill(skill_context)
            if skill and skill.get("instructions"):
                prompt_parts.append(f"=== Skill Context: {skill_context} ===")
                prompt_parts.append(skill["instructions"][:1000])  # Limit size
                prompt_parts.append("")

        # Add RAG context if enabled
        if use_rag:
            relevant_knowledge = await self.rag.retrieve_relevant_knowledge(user_input)
            if relevant_knowledge:
                rag_context = self.rag.get_context_for_prompt(user_input, relevant_knowledge)
                prompt_parts.append(rag_context)
                prompt_parts.append("")

        # Add user input
        prompt_parts.append(f"User Query: {user_input}")

        return "\n".join(prompt_parts)

    def _get_agent_system_prompt(self, agent_name: str) -> str:
        """Get the system prompt for an agent from database"""
        # This would query the database for the agent's system prompt
        # For now, return a default
        default_prompts = {
            "Analyzer Agent": "You are an expert AI campaign analyzer. Analyze ad campaigns, provide insights, and suggest optimizations.",
            "Keyword Agent": "You are an expert keyword optimization AI. Analyze keywords, suggest improvements, and identify trends."
        }
        return default_prompts.get(agent_name, "You are a helpful AI assistant.")

    async def _stream_response(self, messages: List[Dict], client_id: str) -> str:
        """Stream response from OpenRouter API"""
        try:
            logger.info(f"Starting streaming for client {client_id}")
            
            full_response = ""
            token_count = 0
            
            async for token in self.openrouter.stream_chat_completion(messages):
                token_count += 1
                full_response += token
                
                # Stream token to client
                await self.connection_manager.stream_token(
                    token,
                    client_id,
                    "token"
                )
            
            logger.info(f"Streaming complete. Total tokens: {token_count}, Response length: {len(full_response)}")
            return full_response

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            logger.exception(e)
            
            # Fallback to non-streaming
            logger.info("Falling back to non-streaming response")
            try:
                response = await self.openrouter.get_chat_completion(messages, stream=False)
                
                # Send response as single token
                if response:
                    await self.connection_manager.stream_token(
                        response,
                        client_id,
                        "token"
                    )
                
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return f"Error: {str(e)}"

# Global instance
agent_runner = AgentRunner()
