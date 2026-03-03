from generators.hardcoded import HardcodedGenerator
from generators.openai_gen import OpenAIGenerator
from unittest.mock import MagicMock

def test_hardcoded_generator():
    gen = HardcodedGenerator()
    preferences = {"categories": ["social"], "estimated_cost": "minimal", "goal": "fun"}
    result = gen.generate(preferences)
    
    assert "title" in result
    assert "description" in result
    assert "reward_xp" in result
    assert isinstance(result["reward_xp"], int)

def test_openai_generator_mock():
    # Mocking OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"title": "Mock Quest", "description": "Mock Description", "reward_xp": 100, "tags": ["mock"]}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    gen = OpenAIGenerator(api_key="fake_key")
    gen.client = mock_client
    
    preferences = {"categories": ["social"], "estimated_cost": "minimal", "goal": "fun"}
    result = gen.generate(preferences)
    
    assert result["title"] == "Mock Quest"
    assert result["description"] == "Mock Description"
    assert result["reward_xp"] == 100
    mock_client.chat.completions.create.assert_called_once()
