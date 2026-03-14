import asyncio
from playwright.async_api import async_playwright
from .models.lead import BusinessLead

class BrowserAgent:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        print("[Browser] Trình duyệt đã khởi động với chế độ Stealth.")

    async def search_google_maps(self, keyword: str, location: str):
        page = await self.context.new_page()
        search_url = f"https://www.google.com/maps/search/{keyword}+{location}"
        await page.goto(search_url)
        print(f"[Browser] Đang tìm kiếm: {keyword} tại {location}")
        
        # Logic scroll và quét danh sách sẽ được triển khai ở đây
        await asyncio.sleep(5) 
        
        await page.close()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
        print("[Browser] Trình duyệt đã đóng.")
