import asyncio
from typing import List
from .models.lead import BusinessLead, ScrapingTask
from .engine.browser import BrowserAgent
from .engine.ai_services import AIService

class ScrapingCoordinator:
    def __init__(self, ai_service: AIService, headless: bool = True):
        self.ai_service = ai_service
        self.browser_agent = BrowserAgent(headless=headless)
        self.results: List[BusinessLead] = []

    async def run_task(self, task: ScrapingTask):
        print(f"[Coordinator] Bắt đầu chiến dịch quét cho {len(task.keywords)} từ khóa...")
        await self.browser_agent.start()
        
        try:
            for keyword in task.keywords:
                for location in task.locations:
                    # Giả lập quét dữ liệu
                    print(f"[Coordinator] Đang xử lý: {keyword} tại {location}")
                    await self.browser_agent.search_google_maps(keyword, location)
                    
                    # Giả lập lấy được 1 lead
                    sample_lead = BusinessLead(
                        name="Cửa hàng mẫu",
                        phone="0123456789",
                        website="http://example.com",
                        address=f"{location}, Việt Nam"
                    )
                    
                    if task.deep_scan and sample_lead.website:
                        intel = await self.ai_service.extract_business_intel("", sample_lead.website)
                        sample_lead.emails = intel.get("emails", [])
                        sample_lead.socials.facebook = intel.get("socials", {}).get("facebook")
                        sample_lead.status = "Enriched"
                    
                    self.results.append(sample_lead)
                    print(f"[Coordinator] Đã thu thập: {sample_lead.name}")

        finally:
            await self.browser_agent.stop()
        
        print(f"[Coordinator] Hoàn tất chiến dịch. Tổng cộng: {len(self.results)} leads.")
        return self.results
