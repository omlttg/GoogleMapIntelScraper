import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.engine.ai_services import OpenAIService

@pytest.mark.asyncio
async def test_openai_extract_intel():
    # Mocking the entire AsyncOpenAI class
    with patch("core.engine.ai_services.AsyncOpenAI") as MockClient:
        # Setup mock client instance
        mock_client_instance = MockClient.return_value
        mock_client_instance.chat.completions.create = AsyncMock()
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"emails": ["test@email.com"], "socials": {"facebook": "fb.com/test"}}'))
        ]
        mock_client_instance.chat.completions.create.return_value = mock_response
        
        service = OpenAIService(api_key="test_key")
        result = await service.extract_business_intel("<html></html>", "http://test.com")
        
        assert result["emails"] == ["test@email.com"]
        assert result["socials"]["facebook"] == "fb.com/test"

@pytest.mark.asyncio
async def test_openai_extract_intel_error():
    with patch("core.engine.ai_services.AsyncOpenAI") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        service = OpenAIService(api_key="test_key")
        result = await service.extract_business_intel("<html></html>", "http://test.com")
        
        assert result["emails"] == []
        assert "socials" in result
