import json
from abc import abstractmethod
from typing import Dict, Any, List
from .base import BaseGenerator

class AIGenerator(BaseGenerator):
    def _create_prompt(self, preferences: Dict[str, Any]) -> str:
        """
        Creates a prompt for the AI based on user preferences.
        """
        categories = preferences.get("categories", "any")
        estimated_cost = preferences.get("estimated_cost", "minimal")
        goal = preferences.get("goal", "fun")
        
        prompt = f"""
Generate 1 sidequest considering these user preferences:
- Categories: {categories}
- Estimated Cost: {estimated_cost}
- Primary Goal: {goal}

Style Guide:
- Description MUST be extremely concise (1-3 sentences maximum).
- Tone should be encouraging and action-oriented.
- Example: "Drink 3 full glasses of water before doing anything else today. Your body needs it!"

XP Reward Guidelines:
- Assign a `reward_xp` value between 50 and 500 based on the effort and difficulty of the task.
- 50-100 XP: Minimal effort, quick tasks (e.g., hydration, 5-min stretch).
- 101-300 XP: Moderate effort, takes 15-60 mins (e.g., long walk, cleaning a room).
- 301-500 XP: Significant effort or commitment (e.g., learning a new skill session, challenging workout).

Other constraints:
- The task should be achievable within a day.
- It should be safe and ethical.

Return the response ONLY as a structured JSON with the following schema:
{{
    "title": "A catchy title",
    "description": "Short 1-3 sentence description",
    "reward_xp": 100
}}
"""
        return prompt.strip()

    def _validate_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates that the AI response has the required fields.
        """
        required_fields = ["title", "description", "reward_xp"]
        for field in required_fields:
            if field not in response_data:
                raise ValueError(f"Missing required field in AI response: {field}")
        
        # Ensure reward_xp is an integer
        if not isinstance(response_data["reward_xp"], int):
            try:
                response_data["reward_xp"] = int(response_data["reward_xp"])
            except (ValueError, TypeError):
                response_data["reward_xp"] = 50 # Default fallback
                
        return {
            "title": response_data["title"],
            "description": response_data["description"],
            "reward_xp": response_data["reward_xp"]
        }
