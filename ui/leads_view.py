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
        
        self.export_path_input = ft.TextField(
            label="Đường dẫn lưu file (CSV)",
            value="google_maps_leads.csv",
            hint_text="Nhập tên file hoặc đường dẫn đầy đủ",
            expand=True,
            border_radius=10,
        )
        
        self.search_field = ft.TextField(
            hint_text="Tìm kiếm lead...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            border_radius=10,
        )
        
        # Export Options - In-place menu thay vì Dialog để tránh lỗi OpenGL
        self.export_options_container = ft.Container(
            content=ft.Row([
                ft.ElevatedButton("Tải CSV cục bộ", icon=ft.Icons.DOWNLOAD, on_click=self.export_csv_local_action, bgcolor=ft.Colors.BLUE_900),
                ft.ElevatedButton("Xuất Google Sheets", icon=ft.Icons.TABLE_CHART, on_click=self.export_google_sheets_action, bgcolor=ft.Colors.GREEN_900),
                ft.TextButton("Đóng", on_click=self.close_export_options)
            ], spacing=20),
            visible=False,
            padding=15,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.BLUE_700)
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
                        "XUẤT CSV", 
                        icon=ft.Icons.FILE_DOWNLOAD,
                        on_click=self.handle_export_click,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_700,
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            self.export_options_container, # Thanh menu xuất hiện in-place
            ft.Row([self.export_path_input]),
            ft.Row([self.search_field, ft.ElevatedButton("Lọc", icon=ft.Icons.FILTER_ALT)]),
            ft.Container(
                content=self.vertical_scroll,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=10,
                padding=10,
            )
        ]

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
            await self.app_layout.update_dashboard_stats()
            
        try:
            self.main_page.update()
        except:
            pass

    async def handle_open_link(self, url):
        if url:
            try:
                await self.main_page.launch_url(url)
            except:
                pass

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

    async def handle_export_click(self, e):
        """Hiển thị menu lựa chọn phương thức xuất in-place."""
        print("[UI] Nút 'XUẤT CSV' được nhấn")
        if not self.leads:
            print("[UI] Không có leads để xuất")
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Chưa có dữ liệu để xuất!"), bgcolor=ft.Colors.ORANGE_700)
            self.main_page.snack_bar.open = True
            try:
                self.main_page.update()
            except:
                pass
            return

        self.export_options_container.visible = True
        print("[UI] Đang hiển thị menu lựa chọn Export")
        try:
            self.main_page.update()
        except Exception as ex:
            print(f"[UI] Lỗi update hiện menu: {ex}")

    async def close_export_options(self, e):
        self.export_options_container.visible = False
        try:
            self.main_page.update()
        except:
            pass

    async def export_csv_local_action(self, e):
        print("[UI] Bắt đầu Xuất CSV cục bộ...")
        path = self.export_path_input.value.strip() or "google_maps_leads.csv"
        await self._perform_csv_save(path)

    async def _perform_csv_save(self, path):
        try:
            print(f"[UI] Đang lưu vào: {path}")
            await asyncio.to_thread(export_leads_to_csv, self.leads, path)
            print("[UI] Lưu CSV thành công")
            if self.app_layout:
                self.app_layout.log_activity(f"Đã xuất {len(self.leads)} leads ra file CSV: {os.path.basename(path)}")
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"✅ Đã xuất CSV thành công tại: {path}"), bgcolor=ft.Colors.GREEN_700)
        except Exception as ex:
            print(f"[UI] Lỗi lưu CSV: {ex}")
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"❌ Lỗi: {str(ex)}"), bgcolor=ft.Colors.RED_700)
        
        self.main_page.snack_bar.open = True
        try:
            self.main_page.update()
        except:
            pass

    async def export_google_sheets_action(self, e):
        print("[UI] Bắt đầu Xuất sang Google Sheets...")
        self.main_page.snack_bar = ft.SnackBar(ft.Text("🚀 Đang đẩy dữ liệu lên Google Sheets..."))
        self.main_page.snack_bar.open = True
        try:
            self.main_page.update()
        except:
            pass
        
        try:
            exporter = GoogleSheetsExporter()
            link = await asyncio.to_thread(exporter.export, self.leads)
            print(f"[UI] Xuất Google Sheets thành công: {link}")
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
                ft.Text(f"❌ Lỗi Google Sheets: {error_msg}{hint}"), 
                bgcolor=ft.Colors.RED_700,
                duration=8000
            )
        self.main_page.snack_bar.open = True
        try:
            self.main_page.update()
        except:
            pass
