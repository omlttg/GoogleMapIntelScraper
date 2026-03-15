import flet as ft

class LeadsView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.leads = [] # Lưu danh sách BusinessLead thực tế
        
        # FilePicker để chọn nơi lưu CSV
        self.export_picker = ft.FilePicker(on_result=self.save_file_result)
        
        # Load dữ liệu cũ
        self.load_initial_data()
        
        self.search_field = ft.TextField(
            hint_text="Tìm kiếm lead...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            border_radius=10,
        )
        
        self.table = ft.DataTable(
            border=ft.border.all(1, ft.Colors.GREY_700),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
            columns=[
                ft.DataColumn(ft.Text("Tên doanh nghiệp", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Website", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Trạng thái", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        self.table_container = ft.Column(
            [self.table],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )
        
        self.controls = [
            self.export_picker, # Thêm picker vào controls ảo
            ft.Row(
                [
                    ft.Text("Quản lý Leads", size=32, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        ft.Icons.FILE_DOWNLOAD, 
                        tooltip="Xuất CSV",
                        on_click=lambda _: self.export_picker.save_file(
                            file_name="google_maps_leads.csv",
                            allowed_extensions=["csv"]
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            ft.Row([self.search_field, ft.ElevatedButton("Lọc", icon=ft.Icons.FILTER_ALT)]),
            ft.Container(
                content=self.table_container,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=10,
                padding=10,
            )
        ]

    async def add_lead_row_async(self, lead, save=True):
        self.leads.append(lead) # Lưu lại lead
        new_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(lead.name)),
                ft.DataCell(ft.Text(lead.website or "N/A")),
                ft.DataCell(ft.Text(", ".join(lead.emails) if lead.emails else "N/A")),
                ft.DataCell(ft.Text(lead.status, color=ft.Colors.BLUE if lead.status == "Scraped" else ft.Colors.GREEN)),
                ft.DataCell(ft.IconButton(ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.page.launch_url(lead.gmap_url))),
            ]
        )
        self.table.rows.append(new_row)
        if save:
            self.save_all_leads()
        
        # Cập nhật toàn bộ view thay vì chỉ table để đảm bảo hiển thị
        self.update()

    def add_lead_row(self, lead, save=True):
        # Sync version for initial loading
        self.leads.append(lead)
        new_row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(lead.name)),
                ft.DataCell(ft.Text(lead.website or "N/A")),
                ft.DataCell(ft.Text(", ".join(lead.emails) if lead.emails else "N/A")),
                ft.DataCell(ft.Text(lead.status, color=ft.Colors.BLUE if lead.status == "Scraped" else ft.Colors.GREEN)),
                ft.DataCell(ft.IconButton(ft.Icons.OPEN_IN_NEW, on_click=lambda _: self.page.launch_url(lead.gmap_url))),
            ]
        )
        self.table.rows.append(new_row)
        if save:
            self.save_all_leads()
        # No update() here to avoid mounting errors during init

    def load_initial_data(self):
        from core.utils.persistence_utils import load_leads
        self.leads = load_leads()
        for lead in self.leads:
            self.add_lead_row(lead, save=False)

    def save_all_leads(self):
        from core.utils.persistence_utils import save_leads
        save_leads(self.leads)

    async def save_file_result(self, e):
        if e.path:
            from core.utils.export_utils import export_leads_to_csv
            try:
                export_leads_to_csv(self.leads, e.path)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Đã xuất file thành công tại: {e.path}"), bgcolor=ft.Colors.GREEN_700)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi xuất file: {str(ex)}"), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()
