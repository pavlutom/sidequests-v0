import random
from typing import Dict, Any
from .base import BaseGenerator

# Hardcoded list of sidequests for the MVP
# Later, this will be replaced with an AI generation endpoint
SIDEQUESTS = [
    {
        "title": "The Hydration Challenge",
        "description": "Drink 3 full glasses of water before doing anything else today. Your body needs it!",
        "reward_xp": 50
    },
    {
        "title": "Digital Detox 30",
        "description": "Put your phone in another room and read a book or meditate for exactly 30 minutes.",
        "reward_xp": 100
    },
    {
        "title": "The Stretch Break",
        "description": "Stand up and do a full body stretching routine for 10 minutes. Focus on your back and shoulders.",
        "reward_xp": 40
    },
    {
        "title": "The Compliment Quest",
        "description": "Send a genuine compliment or message of appreciation to a friend or coworker you haven't spoken to in a while.",
        "reward_xp": 75
    },
    {
        "title": "The Micro-Clean",
        "description": "Spend exactly 5 minutes cleaning the most cluttered surface in your immediate vicinity.",
        "reward_xp": 30
    },
    {
        "title": "Step Outside",
        "description": "Go outside for a 15-minute walk without any headphones or music. Just observe your surroundings.",
        "reward_xp": 120
    }
]

class HardcodedGenerator(BaseGenerator):
    def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a random sidequest from a hardcoded list.
        Ignores preferences for now to maintain backward compatibility/fallback.
        """
        quest = random.choice(SIDEQUESTS)
        return {
            "title": quest["title"],
            "description": quest["description"],
            "reward_xp": quest["reward_xp"]
        }
