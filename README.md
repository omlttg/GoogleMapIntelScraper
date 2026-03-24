# G-Map Intel Scraper 🛡️🔍

[🇻🇳 Tiếng Việt](#tiếng-viet) | [🇺🇸 English](#english)

---

<a name="tiếng-viet"></a>
## 🇻🇳 Tiếng Việt

### 1. Giới thiệu & Công năng
**G-Map Intel Scraper** là một giải pháp tự động hóa khai thác dữ liệu doanh nghiệp từ Google Maps. Điểm đột phá so với các công cụ truyền thống là khả năng **tự động phân tích sâu (Deep Scan)**:
- **Khai phá thông tin ẩn**: Sử dụng AI (GPT-4o/Gemini 1.5) để truy cập website doanh nghiệp, tự động nhận diện và trích xuất Email, Facebook, LinkedIn, Instagram... mà Google Maps không có.
- **Tiền xử lý thông minh**: Lọc bỏ các dữ liệu rác, chuẩn hóa định dạng số điện thoại và địa chỉ ngay trong quá trình quét.

### 2. Kiến trúc mã nguồn (Clean Code)
Source code được thiết kế theo các nguyên lý lập trình hiện đại:
- **Factory Pattern**: Quản lý việc khởi tạo các AI Service và Scraping Coordinator một cách linh hoạt, dễ dàng mở rộng thêm các nhà cung cấp AI mới.
- **Asynchronous Initialization**: Toàn bộ quá trình nạp dữ liệu và cấu hình trình duyệt được thực hiện bất đồng bộ (Async), giúp giao diện (UI) luôn mượt mà, không bị treo.
- **State Isolation**: Cô lập trạng thái các ô nhập liệu (Input fields) để tránh lỗi chèn ký tự lạ (Ghost characters) thường gặp trong ứng dụng Flet.

### 3. Hướng dẫn sử dụng chi tiết
1.  **Thiết lập môi trường**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux
    pip install -r requirements.txt
    playwright install chromium
    ```
2.  **Cấu hình API**: 
    - Mở tab **Cấu hình**.
    - Nhập API Key. Ưu tiên **Gemini** nếu bạn cần quét tốc độ cao với chi phí thấp, hoặc **OpenAI** cho độ chính xác tối đa.
3.  **Chạy chiến dịch**:
    - Nhập từ khóa (vd: `Thi công nội thất`) và địa điểm (vd: `Hà Nội`).
    - Nhấn **BẮT ĐẦU CHIẾN DỊCH**. Kết quả sẽ hiển thị ngay lập tức trong bảng dữ liệu.
4.  **Xuất kết quả**:
    - Nhấn **XUẤT DỮ LIỆU**.
    - Chọn **CSV** để lưu trực tiếp vào ổ cứng (đường dẫn mặc định nằm trong bảng điều khiển phía trên).
    - Chọn **Google Sheets** để đẩy dữ liệu lên đám mây (cần file `service_account.json` trong thư mục `data/`).

---

<a name="english"></a>
## 🇺🇸 English

### 1. Introduction & Power
**G-Map Intel Scraper** is a high-performance automation solution for extracting business data from Google Maps. Its superpower lies in its **AI-driven Deep Scan** capability:
- **Discovering Hidden Intel**: Leverages AI (GPT-4o/Gemini 1.5) to browse business websites, automatically identifying and extracting Emails, Facebook, LinkedIn, and Instagram profiles unreachable by standard scrapers.
- **Smart Pre-processing**: Filters out data noise and standardizes phone/address formats on the fly.

### 2. Source Code Architecture (Clean Code)
The project adheres to modern software engineering principles:
- **Factory Pattern**: Centralized management of AI Services and Scraping Coordinators, ensuring easy integration of new AI providers.
- **Asynchronous Initialization**: All heavy operations (browser setup, data loading) are performed asynchronously, keeping the UI responsive and butter-smooth.
- **State Isolation**: Strict isolation of UI input states to prevent common Flet-related input glitches (Ghost characters).

### 3. Detailed Usage Guide
1.  **Environment Setup**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux
    pip install -r requirements.txt
    playwright install chromium
    ```
2.  **API Configuration**: 
    - Open the **Settings** tab.
    - Enter your API Key. Use **Gemini** for fast, low-cost processing, or **OpenAI** for high-precision extraction.
3.  **Running a Campaign**:
    - Enter Keywords (e.g., `Furniture Design`) and Location (e.g., `New York`).
    - Click **START CAMPAIGN**. Results will populate the data table in real-time.
4.  **Exporting Data**:
    - Click **EXPORT DATA**.
    - Use **CSV** for immediate local saving (path controlled in the upper panel).
    - Use **Google Sheets** for cloud storage (requires `service_account.json` in the `data/` folder).

---

## 🛠 Troubleshooting / Khắc phục lỗi

*   **Linux UI Issues**: If the UI doesn't render correctly, run: `LIBGL_ALWAYS_SOFTWARE=1 python ui_main.py`.
*   **Permissions**: Ensure the `data/` directory has write permissions for saving `leads.json` and export results.
