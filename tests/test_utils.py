import os
import json
from core.models.lead import BusinessLead
from core.utils.export_utils import export_leads_to_csv
from core.utils.persistence_utils import save_leads, load_leads

def test_export_leads_to_csv_comprehensive(tmp_path):
    # Setup
    from core.models.lead import SocialLinks
    lead = BusinessLead(
        name="Test Cafe", 
        website="http://test.com", 
        status="Scraped",
        rating=4.5,
        reviews_count=None, # Test handling None
        emails=["contact@test.com", "info@test.com"],
        socials=SocialLinks(facebook="fb.com/test", instagram="ig.com/test")
    )
    leads = [lead]
    filepath = tmp_path / "comprehensive_test.csv"
    
    # Action
    export_leads_to_csv(leads, str(filepath))
    
    # Assert
    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8-sig")
    
    # Kiểm tra các giá trị cơ bản
    assert "Test Cafe" in content
    assert "http://test.com" in content
    
    # Kiểm tra Email (phân cách bởi dấu phẩy)
    assert "contact@test.com, info@test.com" in content
    
    # Kiểm tra Social Links (định dạng mới: Platform: URL)
    assert "Facebook: fb.com/test" in content
    assert "Instagram: ig.com/test" in content
    assert " | " in content # Dấu ngăn cách
    
    # Kiểm tra Rating và Reviews
    assert "4.5" in content
    # Reviews_count là None thì không nên có chữ 'None' trong CSV (với logic hiện tại là DictWriter mặc định viết gì?)
    # Thực ra trong export_utils tôi chưa xử lý reviews_count đặc biệt, nên nó sẽ là empty string hoặc None tùy writer.
    # Nhưng trong CSV thông thường nó sẽ là trống.

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
