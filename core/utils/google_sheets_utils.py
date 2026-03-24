import os
import json
from typing import List
from core.models.lead import BusinessLead
from googleapiclient.discovery import build
from google.oauth2 import service_account

class GoogleSheetsExporter:
    def __init__(self, credentials_path: str = "data/service_account.json"):
        self.credentials_path = credentials_path
        self.service = None
        self.spreadsheet_id = None
        self.drive_service = None

    def _authenticate(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"⚠️ [GoogleSheets] Không tìm thấy file {self.credentials_path}. Vui lòng tải file JSON từ Google Cloud Console và đặt vào thư mục data/.")
        
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            self.service = build('sheets', 'v4', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            raise Exception(f"❌ [GoogleSheets] Lỗi xác thực: {str(e)}. Kiểm tra file JSON hoặc quyền truy cập.")

    def export(self, leads: List[BusinessLead], sheet_title: str = "G-Map Leads Export") -> str:
        """
        Xuất dữ liệu sang Google Sheets và trả về URL chia sẻ.
        """
        if not leads:
            raise ValueError("Không có dữ liệu để xuất sang Google Sheets.")

        self._authenticate()
        
        # 1. Tạo Spreadsheet mới
        spreadsheet_body = {
            'properties': {
                'title': sheet_title
            }
        }
        try:
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
            self.spreadsheet_id = spreadsheet.get('spreadsheetId')
        except Exception as e:
            raise Exception(f"❌ [GoogleSheets] Không thể tạo Spreadsheet: {str(e)}")
        
        # 2. Chuẩn bị dữ liệu
        header = ["Tên doanh nghiệp", "Số điện thoại", "Website", "Địa chỉ", "Đánh giá", "Số nhận xét", "Google Maps URL", "Emails", "Socials", "Trạng thái"]
        values = [header]
        
        for lead in leads:
            # Định dạng Socials cho Google Sheets
            socials_obj = lead.socials
            active_socials = []
            if socials_obj:
                social_dict = socials_obj.model_dump()
                for platform, url in social_dict.items():
                    if url:
                        active_socials.append(f"{platform.capitalize()}: {url}")
            socials_str = " | ".join(active_socials) if active_socials else "N/A"

            values.append([
                str(lead.name or "N/A"),
                str(lead.phone or "N/A"),
                str(lead.website or "N/A"),
                str(lead.address or "N/A"),
                str(lead.rating) if lead.rating is not None else "0.0",
                str(lead.reviews_count) if lead.reviews_count is not None else "0",
                str(lead.gmap_url or "N/A"),
                ", ".join(lead.emails) if lead.emails else "N/A",
                socials_str,
                str(lead.status or "Unknown")
            ])

        # 3. Ghi dữ liệu
        body = {
            'values': values
        }
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range="Sheet1!A1",
                valueInputOption="RAW", body=body).execute()
        except Exception as e:
            raise Exception(f"❌ [GoogleSheets] Lỗi khi ghi dữ liệu: {str(e)}")

        # 4. Thiết lập quyền chia sẻ (Public View)
        try:
            permission = {
                'type': 'anyone',
                'role': 'viewer',
            }
            self.drive_service.permissions().create(fileId=self.spreadsheet_id, body=permission).execute()
        except Exception as e:
            print(f"⚠️ [GoogleSheets] Cảnh báo: Không thể thiết lập quyền chia sẻ công khai: {str(e)}. Bạn cần mở quyền thủ công.")

        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit?usp=sharing"
