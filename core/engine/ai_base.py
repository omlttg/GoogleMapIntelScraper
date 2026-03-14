from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from core.models.lead import BusinessLead

class AIService(ABC):
    """
    Lớp trừu tượng định nghĩa các phương thức mà mọi dịch vụ AI (OpenAI hoặc Local) phải tuân thủ.
    """
    
    @abstractmethod
    async def extract_business_intel(self, html_content: str, website_url: str) -> Optional[dict]:
        """
        Đọc nội dung HTML của website và tìm kiếm Email, Social Links.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Trả về trạng thái hoạt động của dịch vụ AI.
        """
        return "Unknown"
