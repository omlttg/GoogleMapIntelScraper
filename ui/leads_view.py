import flet as ft
import asyncio
import re
import json
from typing import List
from core.utils.export_utils import export_leads_to_csv
from core.utils.google_sheets_utils import GoogleSheetsExporter
from core.utils.persistence_utils import load_leads, save_leads
import os

class LeadsView(ft.Column):
    def __init__(self, page: ft.Page, app_layout=None):
        super().__init__()
        self.main_page = page
        self.app_layout = app_layout
        self.expand = True
        self.leads = [] # Lưu danh sách BusinessLead thực tế
        
        # Tiến trình quét
        self.progress_bar = ft.ProgressBar(width=600, color=ft.Colors.BLUE_700, bgcolor=ft.Colors.GREY_800, visible=False)
        self.status_text = ft.Text(size=14, italic=True, color=ft.Colors.BLUE_200, visible=False)
        
        # Load dữ liệu cũ (Sẽ được gọi async sau khi UI hiện)
        # self.load_initial_data() 
        
        # File Picker removed due to compatibility issues on Linux
        
        self.export_path_input = ft.TextField(
            label="Đường dẫn lưu (Lưu trực tiếp không cần hộp thoại chọn file)",
            value="google_maps_leads.csv",
            hint_text="Nhấn biểu tượng bên phải để chọn nơi lưu",
            expand=True,
            border_radius=10,
            suffix=ft.Icon(ft.Icons.SAVE)
        )
        
        self.search_field = ft.TextField(
            hint_text="Tìm kiếm lead theo tên, số điện thoại hoặc website...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            border_radius=10,
            on_change=self.handle_search_change
        )
        
        self.filter_button = ft.ElevatedButton(
            "Lọc", 
            icon=ft.Icons.FILTER_ALT,
            on_click=self.handle_search_change
        )
        
        # Export Panel - Unified UI for CSV and Google Sheets
        self.export_panel = ft.Container(
            content=ft.Column([
                ft.Text("Cấu hình Xuất dữ liệu", size=18, weight=ft.FontWeight.BOLD),
                self.export_path_input,
                ft.Row([
                    ft.ElevatedButton(
                        "Lưu File CSV", 
                        icon=ft.Icons.SAVE_ALT, 
                        on_click=self.export_csv_local_action, 
                        bgcolor=ft.Colors.BLUE_800,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(padding=15)
                    ),
                    ft.ElevatedButton(
                        "Xuất Google Sheets", 
                        icon=ft.Icons.CLOUD_UPLOAD, 
                        on_click=self.export_google_sheets_action, 
                        bgcolor=ft.Colors.GREEN_800,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(padding=15)
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.GREY_700),
                    ft.TextButton(
                        "Hủy / Đóng", 
                        on_click=self.close_export_options, 
                        style=ft.ButtonStyle(color=ft.Colors.GREY_400)
                    )
                ], spacing=15, alignment=ft.MainAxisAlignment.START),
            ], spacing=15),
            visible=False,
            padding=20,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.BLUE_900),
            margin=ft.margin.only(bottom=15, top=5)
        )
        
        self.table = ft.DataTable(
            border=ft.border.all(1, ft.Colors.GREY_700),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
            column_spacing=20, # Tăng khoảng cách cột để thoáng hơn
            heading_row_height=50,
            data_row_min_height=50,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Tên doanh nghiệp", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Số điện thoại", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Website", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Trạng thái", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        self.table_container = ft.Row(
            [self.table],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )
        
        # Bọc ListView cho scroll dọc
        self.vertical_scroll = ft.ListView(
            [self.table_container],
            expand=True,
            spacing=0,
            padding=0,
        )
        
        self.controls = [
            # self.export_picker, # Không thêm vào controls vì là non-visual
            ft.Row(
                [
                    ft.Text("Quản lý Leads", size=32, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        self.status_text,
                        self.progress_bar,
                    ], spacing=5),
                    ft.ElevatedButton(
                        "XUẤT DỮ LIỆU", 
                        icon=ft.Icons.IOS_SHARE,
                        on_click=self.handle_export_click,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_800,
                            padding=15,
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            self.export_panel, # Bảng điều khiển xuất thống nhất
            ft.Row([self.search_field, self.filter_button]),
            ft.Container(
                content=self.vertical_scroll,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=10,
                padding=10,
            )
        ]

    async def handle_search_change(self, e):
        """Lọc danh sách leads dựa trên từ khóa tìm kiếm."""
        search_query = self.search_field.value.lower().strip()
        
        # Xóa các hàng hiện tại trong bảng
        self.table.rows = []
        
        # Lọc leads từ danh sách gốc self.leads
        filtered_leads = []
        for lead in self.leads:
            if (search_query in lead.name.lower() or 
                (lead.phone and search_query in lead.phone.lower()) or
                (lead.website and search_query in lead.website.lower()) or
                (lead.address and search_query in lead.address.lower())):
                filtered_leads.append(lead)
                self._add_row_to_table_only(lead)
        
        print(f"[UI] Tìm kiếm: '{search_query}' - Tìm thấy {len(filtered_leads)}/{len(self.leads)} leads")
        
        try:
            self.main_page.update()
        except:
            pass

    async def add_lead_row_async(self, lead, save=True):
        self.leads.append(lead) # Lưu lại lead
        new_row = self._create_lead_row(lead)
        self.table.rows.append(new_row)
        if save:
            self.save_all_leads()
        
        # Cập nhật từ Page gốc để đảm bảo đồng bộ UI
        try:
            self.main_page.update()
        except:
            pass

    def add_lead_row(self, lead, save=True):
        # Sync version for initial loading
        self.leads.append(lead)
        new_row = self._create_lead_row(lead)
        self.table.rows.append(new_row)
        if save:
            self.save_all_leads()
        # No update() here to avoid mounting errors during init

    def update_progress(self, current: int, total: int, status: str = None):
        """Cập nhật thanh tiến trình."""
        self.progress_bar.visible = True
        self.status_text.visible = True
        if total > 0:
            self.progress_bar.value = current / total
        else:
            self.progress_bar.value = None # Marquee mode
        
        if status:
            self.status_text.value = status
        else:
            self.status_text.value = f"Đang quét... ({current}/{total} leads)"
            
        try:
            self.main_page.update()
        except:
            pass

    def stop_progress(self, message: str = "Hoàn tất!"):
        """Ẩn thanh tiến trình khi xong."""
        self.progress_bar.value = 1
        self.status_text.value = message
        try:
            self.main_page.update()
        except:
            pass

    async def load_initial_data(self):
        """Tải dữ liệu ban đầu không đồng bộ."""
        from core.utils.persistence_utils import load_leads
        import asyncio
        self.leads = await asyncio.to_thread(load_leads)
        for lead in self.leads:
            self._add_row_to_table_only(lead)
        
        # Đồng bộ Dashboard
        if self.app_layout:
            self.app_layout.log_activity(f"Hệ thống sẵn sàng. Đã tải {len(self.leads)} leads từ bộ nhớ.")
            await self.app_layout.refresh_stats()
            
        try:
            self.main_page.update()
        except:
            pass

    async def handle_open_link(self, url):
        if url:
            try:
                await self.main_page.launch_url(url)
            except Exception as e:
                print(f"[UI] Không thể mở link {url}: {e}")

    def _add_row_to_table_only(self, lead):
        """Hàm phụ trợ để thêm hàng mà không gọi update()."""
        new_row = self._create_lead_row(lead)
        self.table.rows.append(new_row)

    def _create_lead_row(self, lead):
        """Tạo đối tượng DataRow chuẩn cho một lead với kích thước tự co giãn."""
        return ft.DataRow(
            cells=[
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            lead.name, 
                            weight=ft.FontWeight.W_500,
                            size=13,
                            no_wrap=False, # Cho phép xuống dòng nếu tên quá dài
                        ),
                        padding=ft.padding.only(top=5, bottom=5),
                        width=250, # Tăng chiều rộng cơ bản cho tên
                    )
                ),
                ft.DataCell(
                    ft.Text(
                        lead.phone or "N/A", 
                        color=ft.Colors.BLUE_200 if lead.phone else None, 
                        size=13
                    )
                ),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            lead.website or "N/A", 
                            size=12, 
                            color=ft.Colors.GREY_400,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        width=200,
                        tooltip=lead.website if lead.website else None,
                        on_click=lambda _: self.main_page.run_task(self.handle_open_link, lead.website) if lead.website else None
                    )
                ),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            lead.status, 
                            color=ft.Colors.BLUE if lead.status == "Scraped" else ft.Colors.GREEN, 
                            size=12,
                            weight=ft.FontWeight.BOLD
                        ),
                        alignment=ft.Alignment(0, 0)
                    )
                ),
                ft.DataCell(
                    ft.ElevatedButton(
                        "Mở", 
                        icon=ft.Icons.OPEN_IN_NEW, 
                        on_click=lambda _: self.main_page.run_task(self.handle_open_link, lead.gmap_url),
                        style=ft.ButtonStyle(padding=5)
                    )
                ),
            ]
        )

    def save_all_leads(self):
        from core.utils.persistence_utils import save_leads
        save_leads(self.leads)

    def handle_export_click(self, e):
        """Hiển thị/Ẩn bảng điều khiển xuất dữ liệu."""
        if not self.leads:
            print("[UI] Không có leads để xuất")
            self.app_layout.show_snackbar("Chưa có dữ liệu để xuất!", ft.Colors.ORANGE_700)
            return

        self.export_panel.visible = not self.export_panel.visible
        self.app_layout.safe_update()

    def close_export_options(self, e=None):
        """Đóng bảng điều khiển xuất."""
        self.export_panel.visible = False
        self.app_layout.safe_update()

    async def export_csv_local_action(self, e):
        """Lưu file trực tiếp (FilePicker bị vô hiệu hóa để tháo gỡ lỗi trên Linux)."""
        path = self.export_path_input.value.strip() or "google_maps_leads.csv"
        # Báo hiệu đang bắt đầu
        self.app_layout.show_snackbar(f"📁 Đang lưu trực tiếp vào: {path}...", ft.Colors.BLUE_800)
        await self._perform_csv_save(path)

    # on_file_picker_result removed

    async def _perform_csv_save(self, path):
        try:
            print(f"[UI] Đang lưu vào: {path}")
            # Hiển thị feedback đang xử lý
            self.app_layout.show_snackbar(f"⏳ Đang trích xuất và lưu file CSV...", ft.Colors.BLUE_GREY_800)

            await asyncio.to_thread(export_leads_to_csv, self.leads, path)
            print("[UI] Lưu CSV thành công")
            if self.app_layout:
                self.app_layout.log_activity(f"Đã xuất {len(self.leads)} leads ra file CSV: {os.path.basename(path)}")
            self.app_layout.show_snackbar(f"✅ Đã xuất CSV thành công tại: {path}", ft.Colors.GREEN_700)
        except Exception as ex:
            print(f"[UI] Lỗi lưu CSV: {ex}")
            self.app_layout.show_snackbar(f"❌ Lỗi: {str(ex)}", ft.Colors.RED_700)

    async def export_google_sheets_action(self, e):
        print("[UI] Bắt đầu Xuất sang Google Sheets...")
        self.export_panel.visible = False # Ẩn bảng sau khi chọn
        self.app_layout.show_snackbar("🚀 Đang chuẩn bị và tải dữ liệu lên Google Sheets...", ft.Colors.BLUE_800)
        
        try:
            from core.utils.google_sheets_utils import GoogleSheetsExporter
            exporter = GoogleSheetsExporter()
            link = await asyncio.to_thread(exporter.export, self.leads)
            print(f"[UI] Xuất Google Sheets thành công: {link}")
            
            # Helper custom object cho SnackBar có nút bấm không thể đùng show_snackbar mặc định
            self.main_page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Text("✅ Xuất Google Sheets thành công!"),
                    ft.TextButton("MỞ LINK", on_click=lambda _: self.main_page.launch_url(link))
                ]),
                bgcolor=ft.Colors.GREEN_700,
                duration=10000
            )
        except Exception as ex:
            error_msg = str(ex)
            print(f"[UI] Lỗi xuất Google Sheets: {error_msg}")
            
            hint = ""
            if "service_account.json" in error_msg:
                hint = "\n👉 Hướng dẫn: Bạn cần tải file JSON từ Google Cloud Console và đặt tên là 'service_account.json' vào thư mục 'data/'."
            
            self.main_page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ {error_msg}{hint}"), 
                bgcolor=ft.Colors.RED_700,
                duration=8000
            )
        self.main_page.snack_bar.open = True
        try:
            self.main_page.update()
        except:
            pass
