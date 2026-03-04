from typing import Any
from .base import BaseGenerator
from .hardcoded import HardcodedGenerator
from .openai_gen import OpenAIGenerator

def get_generator(generator_type: str, settings: Any) -> BaseGenerator:
    """
    Factory function to get the configured generator.
    """
    if generator_type == "openai":
        if not settings.openai_api_key:
            print("Warning: OpenAI API key not found, falling back to hardcoded generator.")
            return HardcodedGenerator()
        return OpenAIGenerator(api_key=settings.openai_api_key, model=settings.openai_model)
    
    # Default to hardcoded
    return HardcodedGenerator()

# Legacy interface support
_generator_instance: BaseGenerator | None = None

def generate_sidequest(user_id: Any, preferences: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Legacy-compatible interface that uses the configured generator.
    """
    from config import settings
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = get_generator(settings.generator_type, settings)
    
    return _generator_instance.generate(preferences or {})
