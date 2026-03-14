import os
import json
from core.models.lead import BusinessLead
from core.utils.export_utils import export_leads_to_csv
from core.utils.persistence_utils import save_leads, load_leads

def test_export_leads_to_csv(tmp_path):
    # Setup
    lead = BusinessLead(name="Test Cafe", website="http://test.com", status="Scraped")
    leads = [lead]
    filepath = tmp_path / "test.csv"
    
    # Action
    export_leads_to_csv(leads, str(filepath))
    
    # Assert
    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8-sig")
    assert "Test Cafe" in content
    assert "http://test.com" in content

def test_persistence_save_load(tmp_path):
    # Mock DATA_FILE path
    import core.utils.persistence_utils as pu
    original_file = pu.DATA_FILE
    pu.DATA_FILE = str(tmp_path / "leads.json")
    
    leads = [BusinessLead(name="Store A"), BusinessLead(name="Store B")]
    
    try:
        save_leads(leads)
        loaded = load_leads()
        
        assert len(loaded) == 2
        assert loaded[0].name == "Store A"
        assert loaded[1].name == "Store B"
    finally:
        pu.DATA_FILE = original_file
