import flet as ft
import os

def main(page: ft.Page):
    print("[System] Đã vào được hàm main của Page!")
    page.title = "Test Native UI"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add(
        ft.Row(
            [
                ft.Text("NATIVE NỀN TẢNG ĐANG HOẠT ĐỘNG!", size=30, color="green", weight="bold")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )
    page.update()
    print("[System] Đã gọi page.update() thành công!")

if __name__ == "__main__":
    print("[System] Đang khởi chạy cấu hình SIÊU AN TOÀN (Hard Filter)...")
    # Vô hiệu hóa media_kit bằng cả 2 định dạng
    os.environ["FLET_DESKTOP_NO_MEDIA_KIT"] = "true"
    os.environ["FLET_DESKTOP_NO_AUDIO"] = "1"
    os.environ["FLET_LOG"] = "1"
    os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    os.environ["GDK_BACKEND"] = "x11"
    print("[System] Đã thiết lập xong biến môi trường. Gọi ft.app...")
    ft.app(target=main)
