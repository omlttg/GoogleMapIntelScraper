import asyncio
import os
from core.models.lead import ScrapingTask
from core.engine.ai_services import OpenAIService, LocalAIService
from core.engine.coordinator import ScrapingCoordinator

async def main():
    print("=== G-Map Intel Scraper Core Demo ===")
    
    # 1. Cấu hình task
    task = ScrapingTask(
        keywords=["Phòng khám nha khoa"],
        locations=["Quận 1, Hồ Chí Minh"],
        deep_scan=True,
        max_results=5
    )

    # 2. Lựa chọn AI Service (Thường sẽ lấy từ Cài đặt của App)
    # Ở đây giả lập chọn OpenAI
    ai_choice = "openai" # Hoặc "local"
    
    if ai_choice == "openai":
        # Giả lập có API Key
        ai_service = OpenAIService(api_key="sk-xxxx")
    else:
        ai_service = LocalAIService()

    # 3. Chạy Coordinator
    coordinator = ScrapingCoordinator(ai_service=ai_service, headless=True)
    results = await coordinator.run_task(task)

    # 4. Hiển thị kết quả sơ bộ
    print("\n--- Kết quả thu thập được ---")
    for lead in results:
        print(f"Tên: {lead.name} | SĐT: {lead.phone} | Email: {lead.emails} | Facebook: {lead.socials.facebook}")

if __name__ == "__main__":
    asyncio.run(main())
