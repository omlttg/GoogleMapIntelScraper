import json
import re
from openai import AsyncOpenAI
from core.engine.ai_base import AIService
from core.models.lead import BusinessLead

class OpenAIService(AIService):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def extract_business_intel(self, html_content: str, website_url: str) -> dict:
        """
        Sử dụng OpenAI để trích xuất email và socials từ website.
        """
        # Tiền xử lý đơn giản: Lấy text và links để tiết kiệm tokens
        # Loại bỏ script, style
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        # Giới hạn độ dài để tránh lỗi context length
        body_content = clean_html[:8000] 

        prompt = f"""
        Bạn là một chuyên gia trích xuất dữ liệu. Hãy phân tích nội dung HTML của website sau: {website_url}
        Trích xuất thông tin liên hệ bao gồm:
        1. Danh sách Email (phát hiện tất cả email có trong trang).
        2. Liên kết mạng xã hội (Facebook, Instagram).

        Chỉ trả về định dạng JSON như sau:
        {{
            "emails": ["email1", "email2"],
            "socials": {{
                "facebook": "url",
                "instagram": "url"
            }}
        }}
        Nếu không tìm thấy, hãy để danh sách trống hoặc null cho socials.
        Nội dung HTML:
        {body_content}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return data
        except Exception as e:
            print(f"[AI] Lỗi khi gọi OpenAI: {e}")
            return {"emails": [], "socials": {}}

    def get_status(self) -> str:
        return f"OpenAI Service ({self.model}) Ready"

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

class GeminiService(AIService):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        from google import genai
        self.api_key = api_key
        self.model_name = model
        self.client = genai.Client(api_key=api_key)

    async def extract_business_intel(self, html_content: str, website_url: str) -> dict:
        """Sử dụng Gemini (SDK mới) để trích xuất email và socials."""
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL)
        body_content = clean_html[:15000]

        prompt = f"""
        Analyze the HTML content of this website: {website_url}
        Extract contact information:
        1. List of Emails.
        2. Social Media Links (Facebook, Instagram, LinkedIn, TikTok).

        Return ONLY a raw JSON object string:
        {{
            "emails": ["email1", "email2"],
            "socials": {{
                "facebook": "url",
                "instagram": "url",
                "linkedin": "url",
                "tiktok": "url"
            }}
        }}
        HTML Content:
        {body_content}
        """

        try:
            # SDK mới hỗ trợ async tự nhiên qua client.aio
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            # Trích xuất JSON bằng regex để an toàn
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                print(f"[AI] Gemini không trả về JSON hợp lệ cho {website_url}")
                return {"emails": [], "socials": {}}
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"[AI] Lỗi Quota (429): Hết hạn mức Gemini. Vui lòng kiểm tra API Key tại Google AI Studio.")
            else:
                print(f"[AI] Lỗi khi gọi Gemini ({website_url}): {e}")
            return {"emails": [], "socials": {}}

    def get_status(self) -> str:
        return f"Gemini Service ({self.model_name}) Ready"
