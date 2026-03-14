import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.engine.coordinator import ScrapingCoordinator
from core.models.lead import ScrapingTask, BusinessLead

@pytest.mark.asyncio
async def test_coordinator_run_task():
    # Setup Mocks
    mock_ai = AsyncMock()
    mock_ai.extract_business_intel.return_value = {"emails": ["found@email.com"], "socials": {}}
    
    coordinator = ScrapingCoordinator(mock_ai, headless=True)
    
    # Mock BrowserAgent methods
    coordinator.browser_agent.start = AsyncMock()
    coordinator.browser_agent.stop = AsyncMock()
    coordinator.browser_agent.search_google_maps = AsyncMock(return_value=[
        {"name": "Cafe 1", "gmap_url": "http://gmap.com/1", "website": "http://cafe1.com"}
    ])
    coordinator.browser_agent.get_page_content = AsyncMock(return_value="<html>Body</html>")
    
    task = ScrapingTask(keywords=["Cafe"], locations=["Hanoi"], max_results=1, deep_scan=True)
    
    # Action
    results = await coordinator.run_task(task)
    
    # Assert
    assert len(results) == 1
    assert results[0].name == "Cafe 1"
    assert results[0].emails == ["found@email.com"]
    assert results[0].status == "Enriched"
    
    # Verify calls
    coordinator.browser_agent.start.assert_called_once()
    coordinator.browser_agent.search_google_maps.assert_called_once()
    mock_ai.extract_business_intel.assert_called_once()
