import random
import uuid

# Hardcoded list of sidequests for the MVP
# Later, this will be replaced with an AI generation endpoint
SIDEQUESTS = [
    {
        "title": "The Hydration Challenge",
        "description": "Drink 3 full glasses of water before doing anything else today. Your body needs it!"
    },
    {
        "title": "Digital Detox 30",
        "description": "Put your phone in another room and read a book or meditate for exactly 30 minutes."
    },
    {
        "title": "The Stretch Break",
        "description": "Stand up and do a full body stretching routine for 10 minutes. Focus on your back and shoulders."
    },
    {
        "title": "The Compliment Quest",
        "description": "Send a genuine compliment or message of appreciation to a friend or coworker you haven't spoken to in a while."
    },
    {
        "title": "The Micro-Clean",
        "description": "Spend exactly 5 minutes cleaning the most cluttered surface in your immediate vicinity."
    },
    {
        "title": "Step Outside",
        "description": "Go outside for a 15-minute walk without any headphones or music. Just observe your surroundings."
    }
]

def generate_sidequest(user_id: uuid.UUID) -> dict:
    """
    Generates a new sidequest for the user.
    Currently returns a random choice from a hardcoded list.
    """
    # Simply pick a random quest from our list
    quest = random.choice(SIDEQUESTS)
    
    return {
        "title": quest["title"],
        "description": quest["description"]
    }
