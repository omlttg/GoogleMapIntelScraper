import json
from .ai_base import AIService
from .models.lead import BusinessLead

class OpenAIService(AIService):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def extract_business_intel(self, html_content: str, website_url: str) -> dict:
        """
        Gửi yêu cầu đến OpenAI để trích xuất thông tin từ HTML.
        """
        # Đây là phần giả lập (Stub), sẽ tích hợp thư viện openai sau
        print(f"[AI] Đang sử dụng OpenAI ({self.model}) để phân tích {website_url}...")
        return {
            "emails": ["contact@example.com"],
            "socials": {
                "facebook": "fb.com/example",
                "instagram": "ig.com/example"
            }
        }

    def get_status(self) -> str:
        return "OpenAI Service Ready"

class LocalAIService(AIService):
    def __init__(self, endpoint: str = "http://localhost:11434/v1"):
        self.endpoint = endpoint

    async def extract_business_intel(self, html_content: str, website_url: str) -> dict:
        """
        Gửi yêu cầu đến Local LLM (qua Ollama/Llama-cpp) để trích xuất thông tin.
        """
        print(f"[AI] Đang sử dụng Local AI ({self.endpoint}) để phân tích {website_url}...")
        return {
            "emails": ["admin@local-example.com"],
            "socials": {}
        }

    def get_status(self) -> str:
        return "Local AI Service Ready"
