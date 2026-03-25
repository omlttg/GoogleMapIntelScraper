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
        
        # Form Controls - Scraper (Isolating state with Unique Keys & Handlers)
        self.keyword_input = ft.TextField(
            key="sc_keyword", # Explicit Unique Key
            label="Từ khóa tìm kiếm",
            hint_text="Ví dụ: Cafe, Nhà hàng, Spa",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            on_submit=self.start_scraping,
            on_change=self.on_keyword_change,
            on_focus=self.on_keyword_focus,
            value=""
        )
        self.keyword_input.helper_text = "Các từ khóa ngăn cách bởi dấu phẩy"
        self._keyword_val = "" # Private state
        
        self.location_input = ft.TextField(
            key="sc_location", # Explicit Unique Key
            label="Địa điểm quét",
            hint_text="Ví dụ: Quận 1, Hồ Chí Minh",
            prefix_icon=ft.Icons.LOCATION_ON,
            border_radius=10,
            on_submit=self.start_scraping,
            on_change=self.on_location_change,
            on_focus=self.on_location_focus,
            value=""
        )
        self.location_input.helper_text = "Nhập khu vực bạn muốn tìm kiếm"
        self._location_val = "" # Private state
        
        self.max_results_slider = ft.Slider()
        self.max_results_slider.min = 10
        self.max_results_slider.max = 200
        self.max_results_slider.divisions = 19
        self.max_results_slider.label = "{value} leads"
        self.max_results_slider.value = 20
        
        self.deep_scan_switch = ft.Switch()
        self.deep_scan_switch.label = "Kích hoạt AI Deep Scan (Email & Socials)"
        self.deep_scan_switch.value = True
        
        # Form Controls - AI Config
        self.openai_key_input = ft.TextField()
        self.openai_key_input.label = "OpenAI API Key"
        self.openai_key_input.password = True
        self.openai_key_input.can_reveal_password = True
        self.openai_key_input.value = self.config.get("openai_key", "")
        self.openai_key_input.border_radius = 10
        
        self.gemini_key_input = ft.TextField()
        self.gemini_key_input.label = "Gemini API Key"
        self.gemini_key_input.password = True
        self.gemini_key_input.can_reveal_password = True
        self.gemini_key_input.value = self.config.get("gemini_key", "")
        self.gemini_key_input.border_radius = 10
        

        
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
                        ft.TextButton("Lấy OpenAI API Key tại đây", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.app_layout.main_page.launch_url("https://platform.openai.com/api-keys")),
                        self.gemini_key_input,
                        ft.TextButton("Lấy Gemini API Key tại đây", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.app_layout.main_page.launch_url("https://aistudio.google.com/app/apikey")),
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

    def on_keyword_change(self, e):
        """Đồng bộ giá trị từ khóa một cách an toàn."""
        self._keyword_val = self.keyword_input.value
        
    def on_keyword_focus(self, e):
        """Xử lý sự kiện focus để đảm bảo UI không bị kẹt ký tự thừa (lỗi Flet Desktop)."""
        # Đã cải thiện bằng cách sử dụng các handle biệt lập
        pass

    def on_location_change(self, e):
        """Đồng bộ địa điểm tìm kiếm."""
        self._location_val = self.location_input.value

    def on_location_focus(self, e):
        """Xử lý dứt điểm trường hợp nhảy văn bản giữa các trường."""
        # Kiểm tra nếu giá trị hiện tại có dấu hiệu bị chèn nhầm từ trường khác
        if self._keyword_val and self.location_input.value == self._keyword_val:
             self.location_input.value = ""
             self.page.update()



    async def start_scraping(self, e):
        # Reset lỗi
        self.keyword_input.error_text = None
        self.location_input.error_text = None
        self.openai_key_input.error_text = None
        self.gemini_key_input.error_text = None

        keywords = [k.strip() for k in self._keyword_val.split(",") if k.strip()]
        location = self._location_val.strip()
        
        # 1. Kiểm tra Từ khóa & Địa điểm
        has_error = False
        if not keywords:
            self.keyword_input.error_text = "Vui lòng nhập từ khóa!"
            has_error = True
        if not location:
            self.location_input.error_text = "Vui lòng nhập địa điểm!"
            has_error = True
            
        # 2. Kiểm tra API Key (Tự động nhận diện)
        if self.deep_scan_switch.value:
            if not self.openai_key_input.value and not self.gemini_key_input.value:
                self.openai_key_input.error_text = "Bạn phải nhập ít nhất một API Key (OpenAI hoặc Gemini) để dùng Deep Scan!"
                has_error = True
        
        if has_error:
            self.app_layout.safe_update()
            return

        # Start scraping in background
        task = ScrapingTask(
            keywords=keywords,
            locations=[location],
            max_results=int(self.max_results_slider.value),
            deep_scan=self.deep_scan_switch.value
        )
        
        self.app_layout.show_snackbar("Đang khởi động chiến dịch quét...")
        
        # Chuyển sang tab Leads để xem kết quả
        await self.app_layout.nav_change(1)
        
        # Chạy async trực tiếp hoặc qua loop của page
        await self.run_scraping_flow(task)

    async def run_scraping_flow(self, task):
        # Clear old leads
        self.app_layout.leads_view.table.rows.clear()
        self.app_layout.safe_update(self.app_layout.leads_view)
        
        # Tự động nhận diện AI Service dựa trên Key có sẵn qua Factory
        from core.factory import ServiceFactory
        
        # Tạo cấu hình tạm thời từ UI
        current_config = {
            "openai_key": self.openai_key_input.value,
            "gemini_key": self.gemini_key_input.value
        }
        
        ai_service = ServiceFactory.create_ai_service(current_config)
        
        if task.deep_scan and not ai_service:
            print("[AI] Cảnh báo: Không có API Key. Bỏ qua Deep Scan.")
            self.app_layout.show_snackbar("⚠️ Cảnh báo: Thiếu API Key. Tính năng Deep Scan sẽ bị bỏ qua.", ft.Colors.ORANGE_700)
            task.deep_scan = False


        self.app_layout.coordinator.ai_service = ai_service

        async def on_lead_discovered(lead):
            await self.app_layout.leads_view.add_lead_row_async(lead)
            current_count = len(self.app_layout.leads_view.table.rows)
            # Giả định task.max_results là mục tiêu
            self.app_layout.leads_view.update_progress(current_count, task.max_results)
            await self.app_layout.refresh_stats()

        try:
            # Hiện trạng thái khởi động
            self.app_layout.leads_view.update_progress(0, task.max_results, "Đang khởi động trình duyệt...")
            await self.app_layout.coordinator.run_task(task, on_lead_found=on_lead_discovered)
            self.app_layout.leads_view.stop_progress("Chiến dịch hoàn tất! Đã thu thập đủ dữ liệu.")
            self.app_layout.show_snackbar("Hoàn tất chiến dịch quét!", ft.Colors.GREEN_700)
        except Exception as ex:
            self.app_layout.show_snackbar(f"Lỗi: {str(ex)}", ft.Colors.RED_700)

    async def save_api_config(self, e):
        from core.utils.config_utils import save_config
        self.config["openai_key"] = self.openai_key_input.value
        self.config["gemini_key"] = self.gemini_key_input.value
        # active_provider giờ được tự động nhận diện
        save_config(self.config)
        self.app_layout.show_snackbar("Cấu hình API đã được lưu!", ft.Colors.GREEN_700)
