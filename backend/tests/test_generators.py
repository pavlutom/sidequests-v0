import pytest
from unittest.mock import patch, MagicMock
from generators import get_generator, generate_sidequest
from generators.base import BaseGenerator
from generators.hardcoded import HardcodedGenerator
from generators.openai_gen import OpenAIGenerator
from generators.ai_base import AIGenerator

class MockSettings:
    def __init__(self, key=None, model="test-model"):
        self.openai_api_key = key
        self.openai_model = model

def test_get_generator_fallback():
    # Test openai requested but no key
    settings = MockSettings(key=None)
    gen = get_generator("openai", settings)
    assert isinstance(gen, HardcodedGenerator)
    
    # Test unknown type falls back to hardcoded
    gen = get_generator("unknown_type", settings)
    assert isinstance(gen, HardcodedGenerator)

def test_get_generator_openai():
    settings = MockSettings(key="valid-key")
    gen = get_generator("openai", settings)
    assert isinstance(gen, OpenAIGenerator)
    assert gen.model == "test-model"

def test_legacy_generate_interface(monkeypatch):
    import generators
    # Reset singleton
    generators._generator_instance = None
    
    mock_gen = MagicMock()
    mock_gen.generate.return_value = {"title": "Test", "description": "Desc", "reward_xp": 10}
    
    with patch("generators.get_generator", return_value=mock_gen):
        # We need to mock config.settings too if it's imported inside the function
        res = generate_sidequest(user_id="user-123", preferences={"goal": "fun"})
        assert res["title"] == "Test"
        mock_gen.generate.assert_called_once()
        
        # Test default preferences handling (None -> {})
        mock_gen.reset_mock()
        generate_sidequest(user_id="user-123", preferences=None)
        mock_gen.generate.assert_called_with({})

class DummyAIGenerator(AIGenerator):
    def generate(self, preferences):
        pass

def test_ai_base_prompt_creation():
    gen = DummyAIGenerator()
    prompt = gen._create_prompt({"categories": "health", "estimated_cost": "free", "goal": "relax"})
    assert "health" in prompt
    assert "free" in prompt
    assert "relax" in prompt

def test_ai_base_response_validation():
    gen = DummyAIGenerator()
    
    # Valid
    valid = {"title": "T", "description": "D", "reward_xp": 100}
    assert gen._validate_response(valid) == valid
    
    # Invalid type for xp
    invalid_xp = {"title": "T", "description": "D", "reward_xp": "not-a-number"}
    res = gen._validate_response(invalid_xp)
    assert res["reward_xp"] == 50 # Fallback
    
    # String integer for xp
    str_xp = {"title": "T", "description": "D", "reward_xp": "200"}
    res = gen._validate_response(str_xp)
    assert res["reward_xp"] == 200
    
    # Missing field
    missing = {"title": "T"}
    with pytest.raises(ValueError, match="Missing required field"):
        gen._validate_response(missing)

@patch("generators.openai_gen.OpenAI")
def test_openai_generator_success(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"title": "AI Quest", "description": "A generated quest", "reward_xp": 150}'
    mock_client.chat.completions.create.return_value = mock_response
    
    gen = OpenAIGenerator(api_key="test-key")
    res = gen.generate({"goal": "test"})
    
    assert res["title"] == "AI Quest"
    assert res["reward_xp"] == 150
    mock_client.chat.completions.create.assert_called_once()

@patch("generators.openai_gen.OpenAI")
def test_openai_generator_empty_response(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create.return_value = mock_response
    
    gen = OpenAIGenerator(api_key="test-key")
    with pytest.raises(ValueError, match="Empty response"):
        gen.generate({})

@patch("generators.openai_gen.OpenAI")
def test_openai_generator_api_error(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_client.chat.completions.create.side_effect = Exception("API Server Error")
    
    gen = OpenAIGenerator(api_key="test-key")
    with pytest.raises(Exception, match="API Server Error"):
        gen.generate({})
