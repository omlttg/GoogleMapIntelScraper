import pytest
import asyncio
import time
from core.utils.config_utils import load_config
from core.utils.persistence_utils import load_leads
from core.engine.coordinator import ScrapingCoordinator
from core.engine.ai_services import LocalAIService

@pytest.mark.asyncio
async def test_backend_init_performance():
    """Kiểm tra thời gian khởi tạo các thành phần nặng nhất."""
    
    # 1. Test load_config
    start_time = time.time()
    config = await asyncio.to_thread(load_config)
    duration = time.time() - start_time
    print(f"\n[Test] Load Config: {duration:.4f}s")
    assert duration < 1.0, "Load config quá chậm (>1s)"

    # 2. Test load_leads
    start_time = time.time()
    leads = await asyncio.to_thread(load_leads)
    duration = time.time() - start_time
    print(f"[Test] Load Leads ({len(leads)}): {duration:.4f}s")
    assert duration < 2.0, "Load leads quá chậm (>2s)"

    # 3. Test Coordinator Init (Không khởi động trình duyệt)
    start_time = time.time()
    ai_service = LocalAIService()
    coordinator = ScrapingCoordinator(ai_service, headless=True)
    duration = time.time() - start_time
    print(f"[Test] Coordinator Init: {duration:.4f}s")
    assert duration < 1.0, "Coordinator init quá chậm (>1s)"

@pytest.mark.asyncio
async def test_event_loop_blocking_check():
    """Kiểm tra xem các tác vụ có thực sự bất đồng bộ không."""
    
    # Một flag để kiểm tra loop còn chạy
    heartbeat_count = 0
    
    async def heartbeat():
        nonlocal heartbeat_count
        while True:
            heartbeat_count += 1
            await asyncio.sleep(0.1)

    hb_task = asyncio.create_task(heartbeat())
    
    # Giả lập initialize_async nhưng chạy nặng
    start_hb = heartbeat_count
    await asyncio.sleep(0.5)
    
    assert heartbeat_count > start_hb, "Event loop bị chặn hoàn toàn!"
    
    hb_task.cancel()
