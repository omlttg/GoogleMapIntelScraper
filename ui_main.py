import flet as ft
from ui.dashboard_view import DashboardView
from ui.leads_view import LeadsView
from ui.settings_view import SettingsView
from core.engine.coordinator import ScrapingCoordinator
from core.engine.ai_services import OpenAIService
from core.models.lead import ScrapingTask
import os
from core.bootstrap import setup_environment
from core.factory import ServiceFactory

# Thực hiện thiết lập môi trường ngay lập tức
setup_environment()

from dotenv import load_dotenv
import asyncio
load_dotenv()

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.expand = True
        
        # Placeholder cho Coordinator (Sẽ được khởi tạo async)
        self.coordinator = None
        
        # Views
        self.dashboard = DashboardView()
        self.leads_view = LeadsView(page, app_layout=self)
        self.settings_view = SettingsView(self) # Pass app layout to settings
        
        # self.leads_view.file_picker is removed due to Flet version issues
        
        # Navigation Rail (Sidebar)
        self.nav_rail = ft.NavigationRail()
        self.nav_rail.selected_index = 0
        self.nav_rail.label_type = ft.NavigationRailLabelType.ALL
        self.nav_rail.min_width = 100
        self.nav_rail.min_extended_width = 200
        self.nav_rail.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.nav_rail.destinations = [
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="Leads",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Cấu hình",
                ),
            ]
        self.nav_rail.on_change = self.nav_change
        
        self.content_area = ft.Container()
        self.content_area.content = self.dashboard
        self.content_area.expand = True
        self.content_area.padding = 20
        
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area,
        ]
        
    async def initialize_async(self):
        """Khởi tạo các thành phần nặng không đồng bộ để tránh treo UI."""
        print("[System] Bắt đầu khởi tạo không đồng bộ (Async Init)...")
        try:
            from core.utils.config_utils import load_config
            import asyncio
            
            # Đợi một chút để page sẵn sàng
            await asyncio.sleep(0.5)
            
            # 1. Load config
            print("[System] Milestone 1: Tải cấu hình (Config)")
            config = await asyncio.to_thread(load_config)
            
            # 2. Khởi tạo AI & Coordinator qua Factory
            print("[System] Milestone 2: Khởi tạo AI Service & Coordinator qua Factory")
            ai_service = ServiceFactory.create_ai_service(config)
            self.coordinator = ServiceFactory.create_coordinator(ai_service, headless=True)
            
            # 3. Load Leads ngầm
            print("[System] Milestone 3: Tải dữ liệu Leads cũ")
            await self.leads_view.load_initial_data()
            
            # 4. Cập nhật Dashboard
            print("[System] Milestone 4: Refreshing Dashboard stats")
            await self.refresh_stats()
            print("[System] === KHỞI TẠO HOÀN TẤT - APP SẴN SÀNG ===")
            
        except Exception as e:
            import traceback
            print(f"Lỗi khởi tạo: {e}")
            traceback.print_exc()

    async def refresh_stats(self):
        print("[System] Running refresh_stats...")
        count = len(self.leads_view.leads)
        enriched_count = sum(1 for l in self.leads_view.leads if l.status == "Enriched")
        phones_count = sum(1 for l in self.leads_view.leads if l.phone and l.phone != "N/A")
        
        # Cập nhật UI Dashboard qua phương thức mới
        self.dashboard.update_stats(count, phones_count, enriched_count)

    def log_activity(self, message: str):
        """Ghi log hoạt động và hiển thị lên Dashboard."""
        print(f"[Activity] {message}")
        try:
            self.dashboard.add_activity(message)
        except:
            pass

    async def nav_change(self, e):
        # Hỗ trợ cả khi gọi từ UI event hoặc gọi trực tiếp bằng index
        index = e.control.selected_index if hasattr(e, "control") else e
        
        self.nav_rail.selected_index = index
        if index == 0:
            await self.refresh_stats() # Cập nhật số liệu mới nhất khi vào Dashboard
            self.content_area.content = self.dashboard
        elif index == 1:
            self.content_area.content = self.leads_view
        elif index == 2:
            self.content_area.content = self.settings_view
        
        try:
            self.content_area.update()
            self.nav_rail.update()
            self.main_page.update()
        except Exception as ex:
            print(f"[UI] Cảnh báo lỗi cập nhật: {ex}")

async def main(page: ft.Page):
    page.title = "G-Map Intel Scraper"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    
    # Modern Styling
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    
    app_layout = AppLayout(page)
    page.add(app_layout)
    
    # Khởi tạo các thành phần nặng ngầm
    import asyncio
    asyncio.create_task(app_layout.initialize_async())
    
    page.update()

if __name__ == "__main__":
    # Tự động chọn chế độ hiển thị dựa trên biến môi trường FLET_VIEW
    view_mode = os.environ.get("FLET_VIEW", "flet_app")
    
    if view_mode == "web_browser":
        print("[System] Đang khởi chạy ở chế độ TRÌNH DUYỆT WEB...")
        ft.run(main, view=ft.AppView.WEB_BROWSER) 
    else:
        print("[System] Đang khởi chạy ở chế độ NATIVE DESKTOP...")
        ft.run(main)
