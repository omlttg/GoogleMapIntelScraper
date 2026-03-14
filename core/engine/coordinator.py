import asyncio
from typing import List, Any, Optional, Callable
from core.models.lead import BusinessLead, ScrapingTask
from core.engine.browser import BrowserAgent
from core.engine.ai_base import AIService

class ScrapingCoordinator:
    def __init__(self, ai_service: AIService, headless: bool = True):
        self.ai_service = ai_service
        self.browser_agent = BrowserAgent(headless=headless)
        self.results: List[BusinessLead] = []

    async def run_task(self, task: ScrapingTask, on_lead_found: Optional[Callable] = None) -> List[BusinessLead]:
        print(f"[Coordinator] Bắt đầu chiến dịch quét cho {len(task.keywords)} từ khóa...")
        agent = self.browser_agent
        await agent.start()
        
        try:
            for keyword in task.keywords:
                for location in task.locations:
                    print(f"[Coordinator] Đang quét: {keyword} tại {location}")
                    
                    # 1. Quét danh sách cơ bản từ Google Maps
                    raw_results = await self.browser_agent.search_google_maps(
                        keyword, location, max_results=task.max_results
                    )
                    
                    for raw in raw_results:
                        lead = BusinessLead(
                            name=raw["name"],
                            gmap_url=raw["gmap_url"],
                            website=raw.get("website"),
                            status="Scraped"
                        )
                        
                        # 2. Deep Scan nếu cần (Vào website để tìm Email/Social)
                        if task.deep_scan and lead.website:
                            print(f"[Coordinator] Đang thực hiện Deep Scan cho: {lead.name}")
                            html = await self.browser_agent.get_page_content(lead.website)
                            if html:
                                intel = await self.ai_service.extract_business_intel(html, lead.website)
                                lead.emails = intel.get("emails", [])
                                if intel.get("socials"):
                                    lead.socials.facebook = intel.get("socials").get("facebook")
                                    lead.socials.instagram = intel.get("socials").get("instagram")
                                lead.status = "Enriched"
                        
                        self.results.append(lead)
                        if on_lead_found:
                            on_lead_found(lead)
                        print(f"[Coordinator] Đã thu thập: {lead.name}")

        finally:
            await self.browser_agent.stop()
        
        print(f"[Coordinator] Hoàn tất chiến dịch. Tổng cộng: {len(self.results)} leads.")
        return self.results
