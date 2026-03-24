from unittest.mock import MagicMock, patch, PropertyMock
import flet as ft
import asyncio
from ui.settings_view import SettingsView

class MockAppLayout:
    def __init__(self):
        self.main_page = MagicMock()
        self.coordinator = MagicMock()
        self.leads_view = MagicMock()

def test_settings_view_state_isolation():
    """Kiểm tra logic cô lập trạng thái giữa các trường nhập liệu."""
    app_layout = MockAppLayout()
    view = SettingsView(app_layout)
    
    with patch.object(SettingsView, 'page', new_callable=PropertyMock) as mock_page:
        mock_page.return_value = MagicMock()
        
        # 1. Giả lập nhập từ khóa
        view.keyword_input.value = "spa"
        view.on_keyword_change(None)
        assert view._keyword_val == "spa"
        
        # 2. Giả lập lỗi nhảy văn bản (từ khóa nhảy sang ô địa điểm)
        view.location_input.value = "spa"
        view.on_location_focus(None)
        
        # Logic mới phải xóa bỏ nội dung trùng lặp nếu nó bị nhảy nhầm
        assert view.location_input.value == ""
        view.page.update.assert_called()

def test_settings_view_validation():
    """Kiểm tra logic validation trước khi quét."""
    app_layout = MockAppLayout()
    view = SettingsView(app_layout)
    
    with patch.object(SettingsView, 'page', new_callable=PropertyMock) as mock_page:
        mock_page.return_value = MagicMock()
        
        # Trường hợp thiếu từ khóa và địa điểm
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(view.start_scraping(None))
        
        assert view.keyword_input.error_text is not None
        assert view.location_input.error_text is not None
