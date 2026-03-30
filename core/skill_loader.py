import os
import json
from pathlib import Path
from typing import Dict, List, Any
from utils.logger import logger_instance as logger
from db.sqlite_db import db_manager

class SkillLoader:
    """
    Loads and manages skills from the /skills directory.
    Parses SKILL.md files for instructions and _meta.json for configurations.
    """
    def __init__(self, skills_dir="./skills"):
        self.skills_dir = skills_dir
        self.skills_cache = {}
        self.skills_index_file = "./data/skills_index.txt"

    def scan_skills(self) -> Dict[str, Any]:
        """
        Scan the skills directory and load all available skills.
        Returns a dictionary of skill_name -> skill_data.
        """
        logger.info(f"Scanning skills directory: {self.skills_dir}")
        skills = {}

        if not os.path.exists(self.skills_dir):
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return skills

        # Iterate through all subdirectories
        for skill_folder in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_folder)
            
            if not os.path.isdir(skill_path):
                continue

            # Skip __pycache__ and hidden directories
            if skill_folder.startswith('__') or skill_folder.startswith('.'):
                continue

            skill_data = self._load_skill(skill_folder, skill_path)
            if skill_data:
                skills[skill_folder] = skill_data
                logger.info(f"Loaded skill: {skill_folder}")

        self.skills_cache = skills
        self._save_skills_index(skills)
        self._update_db_index(skills)
        
        logger.info(f"Total skills loaded: {len(skills)}")
        return skills

    def _load_skill(self, skill_name: str, skill_path: str) -> Dict[str, Any]:
        """Load a single skill from its directory"""
        skill_data = {
            "name": skill_name,
            "path": skill_path,
            "instructions": "",
            "metadata": {},
            "type": "general"
        }

        # Look for SKILL.md
        skill_md_path = os.path.join(skill_path, "SKILL.md")
        if os.path.exists(skill_md_path):
            try:
                with open(skill_md_path, 'r', encoding='utf-8') as f:
                    skill_data["instructions"] = f.read()
            except Exception as e:
                logger.error(f"Error reading {skill_md_path}: {str(e)}")

        # Look for _meta.json
        meta_json_path = os.path.join(skill_path, "_meta.json")
        if os.path.exists(meta_json_path):
            try:
                with open(meta_json_path, 'r', encoding='utf-8') as f:
                    skill_data["metadata"] = json.load(f)
                    skill_data["type"] = skill_data["metadata"].get("type", "general")
            except Exception as e:
                logger.error(f"Error reading {meta_json_path}: {str(e)}")

        # Only return if we have at least instructions or metadata
        if skill_data["instructions"] or skill_data["metadata"]:
            return skill_data
        
        return None

    def _save_skills_index(self, skills: Dict[str, Any]):
        """Save skills index to a text file for quick reference"""
        try:
            os.makedirs(os.path.dirname(self.skills_index_file), exist_ok=True)
            with open(self.skills_index_file, 'w', encoding='utf-8') as f:
                f.write("=== Qubixa AI Skills Index ===\n\n")
                for skill_name, skill_data in skills.items():
                    f.write(f"Skill: {skill_name}\n")
                    f.write(f"Type: {skill_data.get('type', 'general')}\n")
                    f.write(f"Path: {skill_data['path']}\n")
                    if skill_data.get('metadata'):
                        f.write(f"Metadata: {json.dumps(skill_data['metadata'], indent=2)}\n")
                    f.write("\n" + "="*50 + "\n\n")
            logger.info(f"Skills index saved to {self.skills_index_file}")
        except Exception as e:
            logger.error(f"Error saving skills index: {str(e)}")

    def _update_db_index(self, skills: Dict[str, Any]):
        """Update the database skills_index table"""
        # This would integrate with db_manager to update skills_index table
        # For now, we'll log it
        logger.info(f"Database skills index would be updated with {len(skills)} skills")

    def get_skill(self, skill_name: str) -> Dict[str, Any]:
        """Get a specific skill by name"""
        if not self.skills_cache:
            self.scan_skills()
        return self.skills_cache.get(skill_name)

    def get_all_skills(self) -> Dict[str, Any]:
        """Get all loaded skills"""
        if not self.skills_cache:
            self.scan_skills()
        return self.skills_cache

    def get_skills_by_type(self, skill_type: str) -> List[Dict[str, Any]]:
        """Get all skills of a specific type"""
        if not self.skills_cache:
            self.scan_skills()
        return [skill for skill in self.skills_cache.values() if skill.get('type') == skill_type]

# Global instance
skill_loader = SkillLoader()
