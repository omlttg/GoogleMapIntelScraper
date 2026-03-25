# G-Map Intel Scraper - Changelog 📜
[🇻🇳 Tiếng Việt](#tiếng-viet) | [🇺🇸 English](#english)

---

<a name="tiếng-viet"></a>
## 🇻🇳 Tiếng Việt

### 🎯 Phiên bản hiện tại (Mới nhất)
#### ✨ Tính năng mới & Cải tiến:
- **Clean Code Refactoring**: Tái cấu trúc mã nguồn theo chuẩn Clean Code. Loại bỏ các khối mã gây lỗi tiềm ẩn (`try/except: pass`) và áp dụng nguyên tắc DRY (gộp chung các Snackbar và hàm update UI vào `AppLayout.safe_update`).
- **Unified Export Panel**: Gộp chung tính năng Xuất CSV và Google Sheets vào một bảng điều khiển mở rộng (Panel) thay vì các nút rời rạc.
- **Direct Save CSV**: Khắc phục triệt để lỗi treo UI trên Linux bằng cách loại bỏ `FilePicker` mặc định, chuyển sang lưu trực tiếp bằng cách nhập đường dẫn.
- **AI Factory Pattern**: Dễ dàng chuyển đổi linh hoạt giữa OpenAI và Gemini thông qua `ServiceFactory`. Tự động vô hiệu hóa Deep Scan nếu thiếu API Key.
- **Tương thích google-genai**: Đổi sang `gemini-2.0-flash` để tương thích hoàn toàn với bộ SDK `google-genai` mới, giải quyết lỗi 404.
- **Tài liệu song ngữ**: Mở rộng `README.md` với chỉ dẫn chi tiết, bổ sung thư mục `docs/` chứa nhật ký cập nhật và hướng dẫn kỹ thuật bảo trì.

#### 🐛 Sửa lỗi (Bug Fixes):
- Sửa lỗi crash khởi động ứng dụng do thiếu header trong ListView (đã đổi sang container cuộn an toàn).
- Sửa lỗi `Ghost characters` (ký tự ma) bị chèn nhầm giữa các ô input do xung đột event trên Flet Desktop Linux.
- Sửa lỗi Export CSV ném Exception 21 (Is a directory) do người dùng chọn thư mục thay vì file. 

---

<a name="english"></a>
## 🇺🇸 English

### 🎯 Current Version (Latest)
#### ✨ Features & Improvements:
- **Clean Code Refactoring**: Complete modernization of the codebase adhering to Clean Code rules. Replaced bare `except: pass` blocks with transparent error handling and applied DRY principles via centralized `AppLayout` helpers (`show_snackbar`, `safe_update`).
- **Unified Export Panel**: Consolidated CSV and Google Sheets export functionalities into a clean, collapsible sliding panel.
- **Direct Save CSV**: Completely eliminated severe Linux UI crashing issues by bypassing the native `FilePicker` and implementing a direct-path save mechanism.
- **AI Factory Pattern**: Plug-and-play architecture for OpenAI and Gemini via `ServiceFactory`. Auto-disables Deep Scan if API Keys are missing.
- **google-genai SDK compatibility**: Upgraded default Gemini model to `gemini-2.0-flash` to resolve 404 NOT_FOUND errors with the latest SDK.
- **Bilingual Documentation**: Dramatically expanded `README.md` with deep architectural lore; introduced `docs/` folder containing technical guidelines and changelogs.

#### 🐛 Bug Fixes:
- Fixed an `AttributeError` crashing the app at startup by restructuring the container tree.
- Resolved tricky `Ghost characters` input issues (typing appearing in wrong fields) by strictly isolating the states of Flet UI controls.
- Addressed `[Errno 21] Is a directory` crash in CSV Exporter by enforcing full file-path validation.
