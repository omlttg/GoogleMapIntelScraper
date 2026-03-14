# Báo cáo Nghiên cứu: Google Maps Business Scraper (Cập nhật 2026)

## 0. Định nghĩa Input & Output (Core Requirements)
Để xây dựng một hệ thống "Tình báo doanh nghiệp" (Business Intelligence) hiệu quả, hệ thống cần xử lý các tham số sau:

### Tham số Đầu vào (Input)
- **Từ khóa (Keywords):** Danh sách ngành nghề (vd: "Showroom ô tô", "Phòng khám"). Hỗ trợ import từ file `.txt` hoặc `.csv`.
- **Địa điểm (Location):** 
    - Tên địa danh: Thành phố, Quận/Huyện.
    - Tọa độ (GPS): Latitude/Longitude kèm bán kính (Radius) để quét sâu một khu vực cụ thể.
- **Cấu hình Quét:** 
    - `Deep Scan`: Truy cập website để tìm Email và Social Links.
    - `Max Results`: Giới hạn số lượng lead mỗi từ khóa.
- **Bộ lọc (Filters):** Chỉ lấy lead có SĐT, có Website, hoặc Rating > 4.0.

### Kết quả Đầu ra (Output)
Dữ liệu xuất ra file Excel/CSV hoặc Google Sheets gồm:
- **Thông tin cơ bản:** Tên, SĐT, Website, Địa chỉ, Ngành nghề.
- **Dữ liệu Intel:** Email, Link Facebook/Zalo/Instagram/TikTok/LinkedIn.
- **Metadata:** Rating, Số review, Tọa độ GPS, Link Google Maps.

---

## 1. Phân tích Kỹ thuật Scraping 2026
Việc quét dữ liệu Google Maps hiện nay yêu cầu sự kết hợp giữa tự động hóa trình duyệt và trí tuệ nhân tạo.

| Tiêu chí | Google Places API | AI-Powered Web Scraping |
| :--- | :--- | :--- |
| **Chi phí** | Rất cao (~$17/1000 requests) | Thấp (Chi phí AI Token & Proxy) |
| **Dữ liệu** | Bị giới hạn bởi Google | Không giới hạn, lấy được Email/Social |
| **Độ chính xác** | Tuyệt đối | Rất cao (Nhờ AI nhận diện dữ liệu) |
| **Khả năng mở rộng** | Cao nhưng tốn kém | Rất cao nhờ Autonomous Agents |

---

## 2. Thách thức & Giải pháp Anti-Bot (Advanced 2026)
Google đã nâng cấp hệ thống WAF và nhận diện vân tay trình duyệt. Các giải pháp mới:
- **TLS Fingerprinting:** Sử dụng thư viện như `curl_cffi` trong Python để giả lập chữ ký mạng của các trình duyệt phổ biến (Chrome/Safari), tránh bị chặn ở tầng mạng.
- **AI Behavioral Mimicry:** Thay vì các delay cố định, AI sẽ tạo ra các chuyển động chuột và tốc độ cuộn trang ngẫu nhiên mô phỏng hành vi người dùng thật 100%.
- **Residential Rotating Proxies:** Sử dụng Proxy dân cư thật để tránh bị nhận diện là Datacenter IP.
- **Bypass CAPTCHA:** Tích hợp các dịch vụ giải mã CAPTCHA bằng AI với độ trễ thấp (< 2s).

---

## 3. Quy trình Trích xuất Dữ liệu (Autonomous Flow)
1. **Search & Map:** AI tự động chia nhỏ khu vực tìm kiếm thành các lưới (grid) nhỏ để không bỏ lỡ kết quả.
2. **Infinite Scroll & List Grab:** Playwright tự động cuộn và thu thập toàn bộ danh sách.
3. **Data Enrichment (Deep Scan):** 
    - Worker truy cập website doanh nghiệp.
    - Sử dụng **Vision-based AI** hoặc **LLM** để tìm kiếm Email/Social Links trong header, footer hoặc các trang Contact mà không cần rule-based.
4. **Validation:** Kiểm tra định dạng SĐT và sự tồn tại của Email.

---

## 4. Đề xuất Công nghệ (Stack 2026)
- **Core Engine:** Python + Playwright + `curl_cffi` (Hiệu suất cao nhất).
- **AI Layer:** OpenAI gpt-4o-mini hoặc local LLM (Mistral/Llama) để trích xuất dữ liệu từ các website phức tạp.
- **Frontend:** **Tauri v2** (Rust + React/Next.js) - Cực kỳ nhẹ, bảo mật cao và giao diện Premium.
- **Local DB:** SQLite (Lưu trữ hàng triệu lead trực tiếp trên máy người dùng).

---

## 5. Khía cạnh Pháp lý & Đạo đức
- **Tuân thủ Robots.txt:** Thiết lập độ trễ hợp lý để không gây ảnh hưởng đến máy chủ đối phương.
- **Dữ liệu công khai:** Chỉ thu thập các thông tin doanh nghiệp được niêm yết công khai.
- **EU AI Act 2026:** Lưu trữ nhật ký (traceability logs) về cách dữ liệu được thu thập và sử dụng, đảm bảo tính minh bạch.

---

# Chân dung Sản phẩm: G-Map Intel Scraper

- **Giao diện:** Dashboard hiện đại, hỗ trợ Dark Mode, hiển thị tiến độ quét bằng biểu đồ real-time.
- **Tính năng đặc biệt:**
    - `Smart Filter`: Tìm kiếm Lead chất lượng cao dựa trên AI.
    - `One-Click Export`: Xuất dữ liệu chuyên nghiệp ngay lập tức.
    - `Stealth Mode`: Luôn cập nhật các module chống bot mới nhất.

> [!TIP]
> Bước tiếp theo: Chúng ta sẽ bắt đầu xây dựng **Core Engine** bằng Python để kiểm chứng khả năng vượt rào cản bot của Google Maps.
