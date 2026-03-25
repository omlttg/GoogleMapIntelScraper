# G-Map Intel Scraper - Technical Guidelines 📐
[🇻🇳 Tiếng Việt](#tiếng-viet) | [🇺🇸 English](#english)

---

<a name="tiếng-viet"></a>
## 🇻🇳 Tiếng Việt

### 1. Kiến trúc tổng quan (Architecture Overview)
Dự án được xây dựng dựa trên nguyên lý **Clean Architecture** và tuân thủ các quy tắc **Clean Code** nhằm đảm bảo khả năng mở rộng và dễ bảo trì:
- **`ui/` (Presentation Layer)**: Quản lý giao diện người dùng bằng thư viện `flet`. Chia thành các module độc lập (`dashboard_view.py`, `leads_view.py`, `settings_view.py`) nhằm đảm bảo **Single Responsibility Principle (SRP)**. Các thao tác giao diện được tập trung hóa qua `AppLayout` (DRY).
- **`core/engine/` (Business Logic Layer)**:
  - `ScrapingCoordinator`: Trái tim điều phối quy trình quét đa luồng (Playwright cho quét Maps, AI Service cho Deep Scan).
  - Khởi tạo theo mô hình **Factory Pattern** (`ServiceFactory`), giúp dễ dàng bổ sung các mô hình AI mới (Claude, Llama) trong tương lai mà không sửa đổi code core (Open/Closed Principle).
- **`core/utils/` (Infrastructure Layer)**: Cung cấp các thao tác IO (lưu CSV, tương tác API Google Sheets, JSON persistence).

### 2. Luồng dữ liệu (Data Flow)
1. **Khởi tạo (Async)**: `ui_main.py` kích hoạt `initialize_async()` thực hiện việc nạp API Key, load lịch sử Leads và khởi động trình duyệt ảo một cách bất đồng bộ để UI không bị treo (KISS).
2. **Quét dữ liệu**: Người dùng nhập cấu hình -> `SettingsView` gọi `coordinator.run_task()`.
3. **Deep Scan**: Với mỗi doanh nghiệp tìm thấy, Coordinator sẽ:
   - Nếu có website: Gọi thư viện `google-genai` / `openai` để đọc nội dung website lấy Email, Facebook, Instagram.
   - Trả về đối tượng Pydantic `BusinessLead` chặt chẽ, type-safe (Objects over loose Data Structures).
4. **Hiển thị & Cập nhật**: `LeadsView` bổ sung hàng vào bảng. Mọi tương tác Snackbar và reload UI đều được gọi qua `app_layout.safe_update()` (Error Handling transparent).

### 3. Quy chuẩn bảo trì hệ thống
- **Xử lý lỗi (Error Handling)**: Tuyệt đối không sử dụng `except: pass` tĩnh lặng. Mọi Exception cần được log ra console và hiển thị bằng SnackBar qua hàm `show_snackbar(message, color=ft.Colors.RED_700)`.
- **UI State**: Giữ state (trạng thái ô nhập liệu) tách biệt trong lớp của chính nó (`self._keyword_val`) để xử lý các xung đột phím đặc thù trên trình duyệt Flet Linux.

---

<a name="english"></a>
## 🇺🇸 English

### 1. Architecture Overview
This project is built upon **Clean Architecture** and adheres strictly to **Clean Code** rules to ensure scalability and maintainability:
- **`ui/` (Presentation Layer)**: Manages the user interface using `flet`. Divided into cohesive modules (`dashboard_view.py`, `leads_view.py`, `settings_view.py`) enforcing the **Single Responsibility Principle (SRP)**. UI actions are centralized via `AppLayout` (DRY).
- **`core/engine/` (Business Logic Layer)**:
  - `ScrapingCoordinator`: The core orchestrator managing asynchronous scraping (Playwright for Maps, AI Service for Deep Scan).
  - Instantiated using the **Factory Pattern** (`ServiceFactory`), allowing seamless injection of new AI providers (Claude, Llama) without modifying existing logic (Open/Closed Principle).
- **`core/utils/` (Infrastructure Layer)**: Handles IO operations (CSV dumps, Google Sheets API interaction, and JSON persistence).

### 2. Data Flow
1. **Async Bootstrapping**: `ui_main.py` triggers `initialize_async()` to asynchronously load API Keys, history, and the headless browser, keeping the UI fully responsive (KISS).
2. **Execution**: User inputs config -> `SettingsView` triggers `coordinator.run_task()`.
3. **Deep Scan**: For every discovered business, the Coordinator will:
   - If a website exists: Invoke the `google-genai` / `openai` client to parse the DOM and extract hidden Emails, Facebook, and Instagram links.
   - Return a strictly typed Pydantic `BusinessLead` object (Objects over loose Data Structures).
4. **Rendering & Syncing**: `LeadsView` appends a row to the DataTable. All Snackbar invocations and UI reloads are funnelled through `app_layout.safe_update()` (Transparent Error Handling).

### 3. Maintenance Guidelines
- **Error Handling**: Do not write silent `except: pass` blocks. All Exceptions must be logged locally and bubbled up to the UI via `show_snackbar(message, color=ft.Colors.RED_700)`.
- **UI State Isolation**: Keep raw text-input states local (`self._keyword_val`) to mitigate keyboard event collisions specific to the Flet Linux port.
