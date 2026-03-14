import json
import os

CONFIG_FILE = "data/config.json"

def save_config(config: dict):
    """Lưu cấu hình ứng dụng (API Keys, Preferences)."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_config() -> dict:
    """Tải cấu hình ứng dụng."""
    if not os.path.exists(CONFIG_FILE):
        return {
            "openai_key": "",
            "gemini_key": "",
            "active_provider": "openai", # openai, gemini
            "openai_model": "gpt-4o-mini",
            "gemini_model": "gemini-1.5-flash"
        }
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
