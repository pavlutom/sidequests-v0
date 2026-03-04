import json
import os
from typing import Any
from openai import OpenAI
from .ai_base import AIGenerator

class OpenAIGenerator(AIGenerator):
    def __init__(self, api_key: str, model: str = "gpt-5-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, preferences: dict[str, Any]) -> dict[str, Any]:
        prompt = self._create_prompt(preferences)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative sidequest generator. Keep descriptions very concise (1-3 sentences), similar to an RPG mini-quest."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
                
            response_data = json.loads(content)
            return self._validate_response(response_data)
            
        except Exception as e:
            # Fallback or re-raise
            print(f"Error generating sidequest with OpenAI: {e}")
            raise
