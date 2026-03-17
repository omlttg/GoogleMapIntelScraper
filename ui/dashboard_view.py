import flet as ft

class DashboardView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        
        # Stat Labels
        self.total_leads_stat = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        self.phones_found_stat = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        self.enriched_count_stat = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        
        self.recent_activities_column = ft.Column([
            ft.Text("Chưa có chiến dịch nào được chạy.", color=ft.Colors.GREY_400)
        ], spacing=10)
        
        self.controls = [
            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                controls=[
                    self.stat_card("Tổng số Leads", self.total_leads_stat, ft.Icons.PEOPLE, ft.Colors.BLUE),
                    self.stat_card("Số điện thoại", self.phones_found_stat, ft.Icons.PHONE, ft.Colors.GREEN),
                    self.stat_card("Trích xuất AI", self.enriched_count_stat, ft.Icons.AUTO_AWESOME, ft.Colors.ORANGE),
                ],
                spacing=20,
            ),
            ft.Container(height=20),
            ft.Text("Hoạt động gần đây", size=20, weight=ft.FontWeight.W_500),
            ft.Container(
                content=self.recent_activities_column,
                padding=20,
                border=ft.border.all(1, ft.Colors.GREY_700),
                border_radius=10,
            )
        ]

    def stat_card(self, title, value_control, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=16, color=ft.Colors.GREY_400),
                    value_control,
                ],
                tight=True,
                spacing=5,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
            border_radius=15,
            width=250,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        )

    def update_stats(self, total: int, phones: int, enriched: int):
        self.total_leads_stat.value = str(total)
        self.phones_found_stat.value = str(phones)
        self.enriched_count_stat.value = str(enriched)
        try:
            self.update()
        except:
            pass

    def add_activity(self, message: str):
        if len(self.recent_activities_column.controls) > 0 and \
           isinstance(self.recent_activities_column.controls[0], ft.Text) and \
           "Chưa có" in self.recent_activities_column.controls[0].value:
            self.recent_activities_column.controls.clear()
            
        self.recent_activities_column.controls.insert(0, ft.Text(f"• {message}", size=14))
        if len(self.recent_activities_column.controls) > 5:
            self.recent_activities_column.controls = self.recent_activities_column.controls[:5]
        try:
            self.update()
        except:
            pass
