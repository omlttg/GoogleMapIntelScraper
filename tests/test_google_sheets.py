import pytest
from unittest.mock import MagicMock, patch
from core.models.lead import BusinessLead, SocialLinks
from core.utils.google_sheets_utils import GoogleSheetsExporter

@pytest.fixture
def mock_google_sheets_dependencies():
    with patch("core.utils.google_sheets_utils.service_account.Credentials.from_service_account_file") as mock_creds, \
         patch("core.utils.google_sheets_utils.build") as mock_build, \
         patch("os.path.exists") as mock_exists:
        
        mock_exists.return_value = True
        mock_creds.return_value = MagicMock()
        
        mock_sheets_service = MagicMock()
        mock_drive_service = MagicMock()
        
        # Mock side_effect to return different services based on argument
        def build_side_effect(service_name, version, **kwargs):
            if service_name == "sheets":
                return mock_sheets_service
            return mock_drive_service
            
        mock_build.side_effect = build_side_effect
        
        yield {
            "sheets": mock_sheets_service,
            "drive": mock_drive_service,
            "creds": mock_creds
        }

def test_google_sheets_export_formatting(mock_google_sheets_dependencies):
    # Setup
    exporter = GoogleSheetsExporter(credentials_path="dummy.json")
    leads = [
        BusinessLead(
            name="Cafe X", 
            rating=4.2, 
            reviews_count=100,
            socials=SocialLinks(facebook="fb.com/cafex")
        ),
        BusinessLead(
            name="Store Y", 
            rating=None, 
            reviews_count=None,
            emails=["y@store.com"]
        )
    ]
    
    # Mock Spreadsheet creation return
    mock_google_sheets_dependencies["sheets"].spreadsheets().create().execute.return_value = {"spreadsheetId": "test_id_123"}
    
    # Action
    url = exporter.export(leads)
    
    # Assert
    assert "test_id_123" in url
    
    # Verify values sent to update
    args, kwargs = mock_google_sheets_dependencies["sheets"].spreadsheets().values().update.call_args
    body = kwargs.get("body", {})
    values = body.get("values", [])
    
    # Header check
    assert values[0][0] == "Tên doanh nghiệp"
    
    # Cafe X data check
    cafe_row = values[1]
    assert cafe_row[0] == "Cafe X"
    assert cafe_row[4] == "4.2"
    assert cafe_row[5] == "100"
    assert "Facebook: fb.com/cafex" in cafe_row[8]
    
    # Store Y data check (testing None handling)
    store_row = values[2]
    assert store_row[0] == "Store Y"
    assert store_row[4] == "0.0" # None handling for rating
    assert store_row[5] == "0" # None handling for reviews_count
    assert store_row[7] == "y@store.com"
    assert store_row[8] == "N/A" # No socials
