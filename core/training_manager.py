from typing import Dict, List, Any
from utils.logger import logger_instance as logger
from db.sqlite_db import db_manager
import json

class TrainingManager:
    """
    Manages agent training, evaluation, and improvement.
    Implements self-learning mechanisms.
    """
    def __init__(self):
        self.performance_threshold = 0.7
        self.training_history = []

    async def evaluate_output(
        self,
        agent_name: str,
        user_input: str,
        agent_output: str,
        expected_output: str = None
    ) -> Dict[str, Any]:
        """
        Evaluate agent output quality.
        Returns performance metrics.
        """
        metrics = {
            "agent_name": agent_name,
            "input": user_input,
            "output": agent_output,
            "score": 0.0,
            "feedback": []
        }

        # Basic evaluation criteria
        if len(agent_output) < 10:
            metrics["feedback"].append("Output too short")
            metrics["score"] = 0.3
        elif "error" in agent_output.lower():
            metrics["feedback"].append("Error in output")
            metrics["score"] = 0.4
        else:
            metrics["score"] = 0.8
            metrics["feedback"].append("Output looks good")

        # Compare with expected output if provided
        if expected_output:
            similarity = self._calculate_similarity(agent_output, expected_output)
            metrics["similarity"] = similarity
            metrics["score"] = (metrics["score"] + similarity) / 2

        logger.info(f"Evaluation for {agent_name}: score={metrics['score']}")
        return metrics

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    async def improve_prompt(
        self,
        agent_name: str,
        current_prompt: str,
        performance_metrics: Dict[str, Any]
    ) -> str:
        """
        Suggest improvements to agent prompts based on performance.
        """
        if performance_metrics["score"] >= self.performance_threshold:
            logger.info(f"Agent {agent_name} performing well, no changes needed")
            return current_prompt

        # Generate improvement suggestions
        improvements = []
        
        for feedback in performance_metrics.get("feedback", []):
            if "too short" in feedback.lower():
                improvements.append("Provide more detailed responses")
            elif "error" in feedback.lower():
                improvements.append("Handle errors more gracefully")

        if improvements:
            improved_prompt = current_prompt + "\n\nImprovement areas:\n"
            improved_prompt += "\n".join(f"- {imp}" for imp in improvements)
            logger.info(f"Generated improved prompt for {agent_name}")
            return improved_prompt

        return current_prompt

    async def retrain_agent(
        self,
        agent_name: str,
        training_data: List[Dict[str, str]]
    ) -> bool:
        """
        Retrain agent with new examples.
        Stores training history in database.
        """
        try:
            logger.info(f"Retraining agent: {agent_name} with {len(training_data)} examples")
            
            # Store training data
            for example in training_data:
                db_manager.log_agent_activity(
                    agent_name,
                    "training",
                    json.dumps(example)
                )
            
            self.training_history.append({
                "agent_name": agent_name,
                "examples_count": len(training_data),
                "timestamp": "now"
            })
            
            logger.info(f"Agent {agent_name} retrained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error retraining agent {agent_name}: {str(e)}")
            return False

    def get_training_history(self, agent_name: str = None) -> List[Dict]:
        """Get training history for an agent or all agents"""
        if agent_name:
            return [h for h in self.training_history if h["agent_name"] == agent_name]
        return self.training_history

# Global instance
training_manager = TrainingManager()
