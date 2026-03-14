import csv
from typing import List
from core.models.lead import BusinessLead

def export_leads_to_csv(leads: List[BusinessLead], filepath: str):
    """Xuất danh sách leads ra file CSV."""
    fieldnames = ["name", "website", "address", "phone", "rating", "reviews_count", "gmap_url", "emails", "social_links", "status"]
    
    with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for lead in leads:
            data = lead.model_dump()
            # Chuyển list thành chuỗi để CSV đọc tốt hơn
            data["emails"] = ", ".join(data["emails"])
            data["social_links"] = str(data["socials"]) # Model dùng socials, CSV dùng social_links (tên cũ)
            writer.writerow(data)
