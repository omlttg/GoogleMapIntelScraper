import csv
import os
from typing import List
from core.models.lead import BusinessLead

def export_leads_to_csv(leads: List[BusinessLead], filepath: str):
    """Xuất danh sách leads ra file CSV một cách an toàn."""
    if not leads:
        print("[Export] Cảnh báo: Danh sách leads trống, vẫn tạo file với header.")

    # Đảm bảo thư mục tồn tại
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    fieldnames = ["name", "website", "address", "phone", "rating", "reviews_count", "gmap_url", "emails", "social_links", "status"]
    
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for lead in leads:
                try:
                    data = lead.model_dump()
                    
                    # Xử lý an toàn cho Emails
                    emails_list = data.get("emails") or []
                    data["emails"] = ", ".join(emails_list) if isinstance(emails_list, list) else str(emails_list)
                    
                    # Xử lý an toàn cho Social Links
                    socials_obj = lead.socials
                    active_socials = []
                    if socials_obj:
                        social_dict = socials_obj.model_dump()
                        for platform, url in social_dict.items():
                            if url:
                                active_socials.append(f"{platform.capitalize()}: {url}")
                    data["social_links"] = " | ".join(active_socials) if active_socials else "N/A"
                    
                    # Đảm bảo các trường khác không bị None (tránh lỗi một số trình đọc CSV)
                    data["name"] = data.get("name") or "N/A"
                    data["gmap_url"] = data.get("gmap_url") or "N/A"
                    data["phone"] = data.get("phone") or "N/A"
                    data["website"] = data.get("website") or "N/A"
                    data["address"] = data.get("address") or "N/A"
                    
                    writer.writerow(data)
                except Exception as row_err:
                    print(f"[Export] Lỗi khi xử lý dòng cho lead {getattr(lead, 'name', 'Unknown')}: {row_err}")
                    continue
                    
        print(f"[Export] Đã xuất thành công {len(leads)} leads ra {filepath}")
    except Exception as e:
        print(f"[Export] Lỗi nghiêm trọng khi ghi file CSV: {e}")
        raise e
