import json
import os
from typing import List
from core.models.lead import BusinessLead

DATA_FILE = "data/leads.json"

def save_leads(leads: List[BusinessLead]):
    """Lưu danh sách leads vào tệp JSON."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data = [lead.model_dump() for lead in leads]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_leads() -> List[BusinessLead]:
    """Tải danh sách leads từ tệp JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [BusinessLead(**item) for item in data]
    except Exception as e:
        print(f"[Persistence] Lỗi khi tải dữ liệu: {e}")
        return []
