import flet as ft
import asyncio
from core.models.lead import ScrapingTask

class SettingsView(ft.Column):
    def __init__(self, app_layout):
        super().__init__()
        self.app_layout = app_layout
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        
        # Load Config
        from core.utils.config_utils import load_config
        self.config = load_config()
        
        # Form Controls - Scraper
        self.keyword_input = ft.TextField(
            label="Từ khóa tìm kiếm",
            hint_text="Ví dụ: Cafe, Nhà hàng, Spa",
            helper_text="Các từ khóa ngăn cách bởi dấu phẩy",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            on_submit=self.start_scraping,
            autofocus=True
        )
        
        self.location_input = ft.TextField(
            label="Địa điểm quét",
            hint_text="Ví dụ: Quận 1, Hồ Chí Minh",
            helper_text="Nhập khu vực bạn muốn tìm kiếm",
            prefix_icon=ft.Icons.LOCATION_ON,
            border_radius=10,
            on_submit=self.start_scraping
        )
        
        self.max_results_slider = ft.Slider(
            min=10, max=200, divisions=19,
            label="{value} leads",
            value=20,
        )
        
        self.deep_scan_switch = ft.Switch(label="Kích hoạt AI Deep Scan (Email & Socials)", value=True)
        
        # Form Controls - AI Config
        self.openai_key_input = ft.TextField(
            label="OpenAI API Key",
            password=True,
            can_reveal_password=True,
            value=self.config.get("openai_key", ""),
            border_radius=10,
        )
        
        self.gemini_key_input = ft.TextField(
            label="Gemini API Key",
            password=True,
            can_reveal_password=True,
            value=self.config.get("gemini_key", ""),
            border_radius=10,
        )
        
        self.provider_dropdown = ft.Dropdown(
            label="Nhà cung cấp AI mặc định",
            options=[
                ft.dropdown.Option("openai", "OpenAI (GPT-4o)"),
                ft.dropdown.Option("gemini", "Google Gemini (1.5 Flash)"),
            ],
            value=self.config.get("active_provider", "openai"),
            border_radius=10,
            helper_text="Chọn AI sẽ thực hiện bóc tách website (Deep Scan)."
        )
        
        self.controls = [
            ft.Text("Cấu hình Chiến dịch", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Thông tin cơ bản", size=20, weight=ft.FontWeight.W_500),
                        self.keyword_input,
                        self.location_input,
                        ft.Text("Số lượng lead tối đa mỗi từ khóa:"),
                        self.max_results_slider,
                    ], spacing=20),
                    padding=30
                ),
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Cấu hình API Key (Token)", size=20, weight=ft.FontWeight.W_500),
                        self.openai_key_input,
                        ft.TextButton("Lấy OpenAI API Key tại đây", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.page.launch_url("https://platform.openai.com/api-keys")),
                        self.gemini_key_input,
                        ft.TextButton("Lấy Gemini API Key tại đây", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.page.launch_url("https://aistudio.google.com/app/apikey")),
                        self.provider_dropdown,
                        ft.ElevatedButton(
                            "Lưu Cấu hình API", 
                            icon=ft.Icons.SAVE, 
                            on_click=self.save_api_config
                        ),
                    ], spacing=15),
                    padding=30
                ),
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                "BẮT ĐẦU CHIẾN DỊCH",
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_700,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                on_click=self.start_scraping
            )
        ]

    async def start_scraping(self, e):
        keywords = [k.strip() for k in self.keyword_input.value.split(",") if k.strip()]
        location = self.location_input.value.strip()
        
        if not keywords or not location:
            self.page.snack_bar = ft.SnackBar(ft.Text("Vui lòng nhập từ khóa và địa điểm!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Start scraping in background
        task = ScrapingTask(
            keywords=keywords,
            locations=[location],
            max_results=int(self.max_results_slider.value),
            deep_scan=self.deep_scan_switch.value
        )
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Đang khởi động chiến dịch quét..."))
        self.page.snack_bar.open = True
        
        # Chuyển sang tab Leads để xem kết quả
        await self.app_layout.nav_change(1)
        
        # Chạy async trực tiếp hoặc qua loop của page
        await self.run_scraping_flow(task)

    async def run_scraping_flow(self, task):
        # Clear old leads
        self.app_layout.leads_view.table.rows.clear()
        self.app_layout.leads_view.update()
        
        # Initialize AI Service based on selection
        from core.engine.ai_services import OpenAIService, GeminiService
        
        active_provider = self.provider_dropdown.value
        api_key = self.openai_key_input.value if active_provider == "openai" else self.gemini_key_input.value
        
        if task.deep_scan and not api_key:
            self.app_layout.main_page.snack_bar = ft.SnackBar(
                ft.Text(f"⚠️ Cảnh báo: Thiếu API Key cho {active_provider.upper()}. Tính năng Deep Scan sẽ bị bỏ qua."), 
                bgcolor=ft.Colors.ORANGE_700
            )
            self.app_layout.main_page.snack_bar.open = True
            self.app_layout.main_page.update()
            # Tắt tạm thời deep_scan cho task này
            task.deep_scan = False

        if active_provider == "openai":
            ai_service = OpenAIService(api_key=api_key)
        else:
            ai_service = GeminiService(api_key=api_key)
            
        self.app_layout.coordinator.ai_service = ai_service

        async def on_lead_discovered(lead):
            await self.app_layout.leads_view.add_lead_row_async(lead)
            await self.app_layout.update_dashboard_stats()

        try:
            await self.app_layout.coordinator.run_task(task, on_lead_found=on_lead_discovered)
            self.app_layout.main_page.snack_bar = ft.SnackBar(ft.Text("Hoàn tất chiến dịch quét!"), bgcolor=ft.Colors.GREEN_700)
        except Exception as ex:
            self.app_layout.main_page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi: {str(ex)}"), bgcolor=ft.Colors.RED_700)
        
        self.app_layout.main_page.snack_bar.open = True
        self.app_layout.main_page.update()

    async def save_api_config(self, e):
        from core.utils.config_utils import save_config
        self.config["openai_key"] = self.openai_key_input.value
        self.config["gemini_key"] = self.gemini_key_input.value
        self.config["active_provider"] = self.provider_dropdown.value
        save_config(self.config)
        self.page.snack_bar = ft.SnackBar(ft.Text("Cấu hình API đã được lưu!"), bgcolor=ft.Colors.GREEN_700)
        self.page.snack_bar.open = True
        self.page.update()
