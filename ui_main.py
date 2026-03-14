import flet as ft
from ui.dashboard_view import DashboardView
from ui.leads_view import LeadsView
from ui.settings_view import SettingsView
from core.engine.coordinator import ScrapingCoordinator
from core.engine.ai_services import OpenAIService
from core.models.lead import ScrapingTask
import os
from dotenv import load_dotenv

load_dotenv()

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.expand = True
        
        # Initialize Coordinator with saved config
        from core.utils.config_utils import load_config
        from core.engine.ai_services import OpenAIService, GeminiService
        config = load_config()
        active_provider = config.get("active_provider", "openai")
        api_key = config.get("openai_key") if active_provider == "openai" else config.get("gemini_key")
        
        if active_provider == "openai":
            ai_service = OpenAIService(api_key=api_key or "dummy")
        else:
            ai_service = GeminiService(api_key=api_key or "dummy")
            
        self.coordinator = ScrapingCoordinator(ai_service, headless=True)
        
        # Views
        self.dashboard = DashboardView()
        self.leads_view = LeadsView(page)
        self.settings_view = SettingsView(self) # Pass app layout to settings
        
        # Navigation Rail (Sidebar)
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            destinations=[
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
            ],
            on_change=self.nav_change,
        )
        
        self.content_area = ft.Container(
            content=self.dashboard,
            expand=True,
            padding=20,
        )
        
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area,
        ]
        
        # Cập nhật thông số Dashboard nếu có dữ liệu sẵn (không gọi update() ở đây)
        # self.update_dashboard_stats()

    async def update_dashboard_stats(self):
        count = len(self.leads_view.leads)
        email_count = sum(1 for lead in self.leads_view.leads if lead.emails)
        # Cập nhật UI Dashboard
        self.dashboard.controls[2].controls[0].content.controls[2].value = str(count)
        self.dashboard.controls[2].controls[1].content.controls[2].value = str(email_count)
        if self.dashboard.page:
            self.dashboard.update()

    async def nav_change(self, e):
        # Hỗ trợ cả khi gọi từ UI event hoặc gọi trực tiếp bằng index
        index = e.control.selected_index if hasattr(e, "control") else e
        
        self.nav_rail.selected_index = index
        if index == 0:
            self.content_area.content = self.dashboard
        elif index == 1:
            self.content_area.content = self.leads_view
        elif index == 2:
            self.content_area.content = self.settings_view
        
        self.content_area.update()
        self.nav_rail.update()

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

if __name__ == "__main__":
    ft.app(target=main)
