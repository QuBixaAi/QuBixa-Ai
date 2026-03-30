from typing import Dict, Any, Optional
from core.agent_runner import agent_runner
from core.skill_loader import skill_loader
from utils.excel_processor import excel_processor
from utils.logger import logger_instance as logger
import pandas as pd

class AnalyzerAgent:
    """
    Specialized agent for ad campaign analysis.
    Provides insights, metrics, and optimization suggestions.
    Uses skills from /skills folder and processes Excel data.
    """
    def __init__(self):
        self.agent_name = "Analyzer Agent"
        self.runner = agent_runner
        self.skill_loader = skill_loader
        self.excel_processor = excel_processor

    async def analyze_campaign(
        self,
        campaign_data: Dict[str, Any],
        client_id: str,
        excel_file: Optional[str] = None
    ) -> str:
        """
        Analyze an ad campaign and provide insights.
        
        Args:
            campaign_data: Dictionary containing campaign metrics
            client_id: WebSocket client ID for streaming
            excel_file: Optional path to Excel file with keyword data
        """
        # Load relevant skills
        skills_context = self._load_relevant_skills()
        
        # Process Excel data if provided - use DuckDB analytics
        analysis = None
        predictions = None
        if excel_file:
            analysis = self.excel_processor.analyze_keywords()
            predictions = self.excel_processor.generate_predictions(7)
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            campaign_data, 
            skills_context,
            analysis,
            predictions
        )
        
        # Run agent with skill context
        result = await self.runner.run_agent(
            agent_name=self.agent_name,
            user_input=prompt,
            client_id=client_id,
            skill_context="marketing-mode",  # Use marketing skill
            stream=True
        )
        
        return result

    def _load_relevant_skills(self) -> str:
        """Load relevant skills for ad analysis"""
        skills_text = []
        
        # Try to load marketing and SEO related skills
        skill_names = [
            "marketing-mode",
            "seo-content-writer",
            "market-research-reports"
        ]
        
        for skill_name in skill_names:
            skill = self.skill_loader.get_skill(skill_name)
            if skill and skill.get("instructions"):
                skills_text.append(f"=== {skill_name} ===")
                skills_text.append(skill["instructions"][:500])  # Limit size
                skills_text.append("")
        
        return "\n".join(skills_text) if skills_text else ""

    def _build_analysis_prompt(
        self, 
        campaign_data: Dict[str, Any],
        skills_context: str,
        excel_analysis: Optional[Dict] = None,
        predictions: Optional[Dict] = None
    ) -> str:
        """Build a detailed analysis prompt from campaign data"""
        prompt_parts = []
        
        # Add skills context
        if skills_context:
            prompt_parts.append("=== AVAILABLE SKILLS & KNOWLEDGE ===")
            prompt_parts.append(skills_context)
            prompt_parts.append("")
        
        # Add Excel analysis if available
        if excel_analysis and predictions:
            prompt_parts.append(self.excel_processor.format_for_agent(excel_analysis, predictions))
            prompt_parts.append("")
        
        # Add campaign data
        if campaign_data:
            prompt_parts.append("=== CAMPAIGN DATA ===")
            for key, value in campaign_data.items():
                prompt_parts.append(f"{key}: {value}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "=== ANALYSIS REQUIREMENTS ===",
            "Using the skills and data provided above, please provide:",
            "",
            "1. 📊 PERFORMANCE SUMMARY",
            "   - Current campaign health score (0-100)",
            "   - Key metrics analysis",
            "",
            "2. 💰 MONEY-SAVING OPPORTUNITIES",
            "   - Identify wasteful spending",
            "   - Budget optimization strategies",
            "   - Estimated savings amount",
            "",
            "3. 🎯 KEYWORD OPTIMIZATION",
            "   - High-performing keywords to boost",
            "   - Low-performing keywords to pause/optimize",
            "   - New keyword suggestions",
            "",
            "4. 📈 PREDICTIONS & FORECASTS",
            "   - 7-day performance forecast",
            "   - Expected ROI improvements",
            "   - Risk factors to monitor",
            "",
            "5. ✅ ACTION PLAN",
            "   - Prioritized recommendations",
            "   - Implementation steps",
            "   - Expected timeline and results",
            "",
            "Format your response in a clean, structured way with clear sections and bullet points."
        ])
        
        return "\n".join(prompt_parts)

# Global instance
analyzer_agent = AnalyzerAgent()
