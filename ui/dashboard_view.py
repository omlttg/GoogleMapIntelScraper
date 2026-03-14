import flet as ft

class DashboardView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        
        self.controls = [
            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                controls=[
                    self.stat_card("Tổng số Leads", "0", ft.Icons.PEOPLE, ft.Colors.BLUE),
                    self.stat_card("Email tìm thấy", "0", ft.Icons.EMAIL, ft.Colors.GREEN),
                    self.stat_card("Tỷ lệ phản hồi", "0%", ft.Icons.ANALYTICS, ft.Colors.ORANGE),
                ],
                spacing=20,
            ),
            ft.Container(height=20),
            ft.Text("Hoạt động gần đây", size=20, weight=ft.FontWeight.W_500),
            ft.Container(
                content=ft.Text("Chưa có chiến dịch nào được chạy.", color=ft.Colors.GREY_400),
                padding=20,
                border=ft.border.all(1, ft.Colors.GREY_700),
                border_radius=10,
            )
        ]

    def stat_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=16, color=ft.Colors.GREY_400),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
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
