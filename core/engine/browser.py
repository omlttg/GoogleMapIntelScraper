import asyncio
from typing import List, Optional, Any, Dict, cast, Union
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright, ElementHandle
from core.models.lead import BusinessLead

class BrowserAgent:
    def __init__(self, headless: bool = True):
        self.headless: bool = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright: Optional[Playwright] = None

    async def start(self) -> None:
        p_obj: Playwright = await async_playwright().start()
        self.playwright = p_obj
        
        # Local guarding for browser
        browser_obj: Browser = await p_obj.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.browser = browser_obj
        
        # Local guarding for context
        context_obj: BrowserContext = await browser_obj.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        self.context = context_obj
        print("[Browser] Trình duyệt đã khởi động với chế độ Stealth.")

    async def search_google_maps(self, keyword: str, location: str, max_results: int = 20) -> List[Dict[str, Any]]:
        ctx: Optional[BrowserContext] = self.context
        if ctx is None:
            print("[Browser] Lỗi: Context chưa được khởi tạo.")
            return []

        page: Page = await ctx.new_page()
        search_url: str = f"https://www.google.com/maps/search/{keyword}+{location}"
        await page.goto(search_url)
        print(f"[Browser] Đang tìm kiếm: {keyword} tại {location}")
        
        results: List[Dict[str, Any]] = []
        try:
            # Chờ danh sách kết quả hiển thị
            list_selector: str = "div[role='feed']"
            await page.wait_for_selector(list_selector, timeout=15000)
            
            # Logic scroll vô hạn
            h_obj: Any = await page.evaluate(f'document.querySelector("{list_selector}").scrollHeight')
            last_height: int = cast(int, h_obj) if h_obj else 0
            results_count_int: int = 0
            
            max_res: int = cast(int, max_results)
            
            while results_count_int < max_res:
                # Cuộn xuống cuối danh sách
                await page.evaluate(f'document.querySelector("{list_selector}").scrollTo(0, document.querySelector("{list_selector}").scrollHeight)')
                await asyncio.sleep(3.0)
                
                # Trích xuất các thẻ doanh nghiệp hiện có
                leads_elements: List[ElementHandle] = await page.query_selector_all('div[role="article"]')
                
                # Duyệt qua các phần tử mới bằng index để tránh lỗi slicing
                num_leads: int = len(leads_elements)
                current_idx: int = int(results_count_int)
                
                for i in range(current_idx, num_leads):
                    if results_count_int >= max_res:
                        break
                        
                    el: ElementHandle = leads_elements[i]
                    # Tìm tên doanh nghiệp
                    name_el: Optional[ElementHandle] = await el.query_selector('div.fontHeadlineSmall')
                    if name_el:
                        name: str = await name_el.inner_text()
                        
                        # Link gmap & Website
                        link_el: Optional[ElementHandle] = await el.query_selector('a[href*="/maps/place/"]')
                        gmap_url: Optional[str] = await link_el.get_attribute('href') if link_el else None
                        
                        # Website
                        web_el: Optional[ElementHandle] = await el.query_selector('a[data-value="Website"]')
                        website: Optional[str] = await web_el.get_attribute('href') if web_el else None
                        
                        results.append({
                            "name": name,
                            "gmap_url": gmap_url,
                            "website": website
                        })
                        results_count_int = cast(int, results_count_int) + 1
                
                new_h_obj: Any = await page.evaluate(f'document.querySelector("{list_selector}").scrollHeight')
                new_height: int = cast(int, new_h_obj) if new_h_obj else 0
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            print(f"[Browser] Lỗi khi quét: {str(e)}")
            
        await page.close()
        return results

    async def get_page_content(self, url: str) -> str:
        """Tải nội dung website để AI phân tích."""
        if self.context is None:
            return ""
            
        ctx: BrowserContext = cast(BrowserContext, self.context)
        page: Page = await ctx.new_page()
        
        result_content: str = ""
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            result_content = await page.content()
        except Exception as e:
            print(f"[Browser] Không thể truy cập {url}: {e}")
            result_content = ""
        finally:
            await page.close()
            
        return str(result_content)

    async def stop(self) -> None:
        b: Optional[Browser] = self.browser
        if b is not None:
            await b.close()
        
        p: Optional[Playwright] = self.playwright
        if p is not None:
            await p.stop()
            
        print("[Browser] Trình duyệt đã đóng.")
