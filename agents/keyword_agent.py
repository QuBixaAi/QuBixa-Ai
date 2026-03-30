from typing import Dict, Any, List
from core.agent_runner import agent_runner
from utils.logger import logger_instance as logger

class KeywordAgent:
    """
    Specialized agent for keyword optimization and trend analysis.
    """
    def __init__(self):
        self.agent_name = "Keyword Agent"
        self.runner = agent_runner

    async def optimize_keywords(
        self,
        keywords: List[str],
        context: str,
        client_id: str
    ) -> str:
        """
        Analyze and optimize keywords for better performance.
        
        Args:
            keywords: List of current keywords
            context: Campaign or industry context
            client_id: WebSocket client ID for streaming
        """
        prompt = self._build_optimization_prompt(keywords, context)
        
        result = await self.runner.run_agent(
            agent_name=self.agent_name,
            user_input=prompt,
            client_id=client_id,
            stream=True
        )
        
        return result

    async def analyze_trends(
        self,
        industry: str,
        client_id: str
    ) -> str:
        """Analyze keyword trends for a specific industry"""
        prompt = f"""
        Analyze current keyword trends for the {industry} industry.
        
        Provide:
        1. Top trending keywords
        2. Emerging search patterns
        3. Seasonal considerations
        4. Competitive keyword opportunities
        """
        
        result = await self.runner.run_agent(
            agent_name=self.agent_name,
            user_input=prompt,
            client_id=client_id,
            stream=True
        )
        
        return result

    def _build_optimization_prompt(self, keywords: List[str], context: str) -> str:
        """Build keyword optimization prompt"""
        prompt_parts = [
            f"Optimize the following keywords for {context}:",
            "",
            "Current keywords:",
        ]
        
        for i, keyword in enumerate(keywords, 1):
            prompt_parts.append(f"{i}. {keyword}")
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "1. Keyword performance assessment",
            "2. Suggested improvements or alternatives",
            "3. Long-tail keyword opportunities",
            "4. Negative keywords to exclude"
        ])
        
        return "\n".join(prompt_parts)

# Global instance
keyword_agent = KeywordAgent()
