from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class SocialLinks(BaseModel):
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None
    zalo: Optional[str] = None

class BusinessLead(BaseModel):
    name: str = Field(..., description="Tên doanh nghiệp")
    phone: Optional[str] = Field(None, description="Số điện thoại liên hệ")
    website: Optional[str] = Field(None, description="Địa chỉ website")
    address: Optional[str] = Field(None, description="Địa chỉ vật lý")
    category: Optional[str] = Field(None, description="Ngành nghề kinh doanh")
    rating: Optional[float] = Field(None, description="Điểm đánh giá trung bình")
    reviews_count: Optional[int] = Field(None, description="Số lượng đánh giá")
    
    # Dữ liệu Intel thu thập thêm
    emails: List[str] = Field(default_factory=list, description="Danh sách email liên hệ")
    socials: SocialLinks = Field(default_factory=SocialLinks, description="Liên kết mạng xã hội")
    
    # Metadata
    location_gps: Optional[dict] = Field(None, description="Tọa độ {'lat': float, 'lng': float}")
    gmap_url: Optional[str] = Field(None, description="Link trực tiếp trên Google Maps")
    status: str = Field("Pending", description="Trạng thái xử lý (Pending, Scraped, Enriched, Failed)")

class ScrapingTask(BaseModel):
    keywords: List[str]
    locations: List[str]
    deep_scan: bool = False
    max_results: int = 100
