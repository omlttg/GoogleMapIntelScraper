from typing import Optional
from core.engine.ai_services import OpenAIService, GeminiService, LocalAIService
from core.engine.coordinator import ScrapingCoordinator
from core.engine.ai_base import AIService

class ServiceFactory:
    """
    Factory Pattern để khởi tạo các dịch vụ AI và Coordinator một cách tập trung.
    Giúp code CLEAN và dễ bảo trì hơn.
    """
    
    @staticmethod
    def create_ai_service(config: dict) -> Optional[AIService]:
        """Khởi tạo AI Service dựa trên cấu hình."""
        openai_key = config.get("openai_key")
        gemini_key = config.get("gemini_key")
        
        # Tự động chọn nhà cung cấp nếu có API Key
        if openai_key:
            print("[Factory] Khởi tạo OpenAI Service")
            return OpenAIService(api_key=openai_key, model=config.get("openai_model", "gpt-4o-mini"))
        elif gemini_key:
            print("[Factory] Khởi tạo Gemini Service")
            return GeminiService(api_key=gemini_key, model=config.get("gemini_model", "gemini-1.5-flash"))
        else:
            # Fallback về Local AI hoặc None
            print("[Factory] Cảnh báo: Không có API Key. Sử dụng Local AI hoặc Chế độ Offline.")
            return None # Trả về None để caller tự xử lý fallback

    @staticmethod
    def create_coordinator(ai_service: Optional[AIService] = None, headless: bool = True) -> ScrapingCoordinator:
        """Khởi tạo ScrapingCoordinator."""
        # Nếu không có ai_service, dùng LocalAIService làm mặc định để không bị crash
        service = ai_service or LocalAIService()
        return ScrapingCoordinator(ai_service=service, headless=headless)
