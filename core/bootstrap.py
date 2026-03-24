import os
from dotenv import load_dotenv

def setup_environment():
    """
    Thiết lập các biến môi trường và cấu hình hệ thống ban đầu.
    Giúp ứng dụng chạy ổn định trên nhiều nền tảng (đặc biệt là Linux).
    """
    load_dotenv()
    
    # 1. Khắc phục lỗi treo trên Linux Native Desktop (Flet/Skia)
    os.environ["FLET_LOG"] = "1"
    os.environ["FLET_DESKTOP_NO_MEDIA_KIT"] = "true"
    os.environ["FLET_DESKTOP_NO_AUDIO"] = "1"
    
    # Ép buộc dùng X11 thay vì Wayland (thường gây treo trên một số bản phân phối Linux)
    if os.name != 'nt':
        os.environ["GDK_BACKEND"] = "x11"
        # Ép buộc Software Rendering để fix lỗi Driver GPU
        os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    
    print("[Bootstrap] Môi trường đã được thiết lập.")
