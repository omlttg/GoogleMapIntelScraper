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

    def _authenticate(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Không tìm thấy file {self.credentials_path}. Vui lòng cấu hình Google Service Account.")
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        self.service = build('sheets', 'v4', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)

    def export(self, leads: List[BusinessLead], sheet_title: str = "G-Map Leads Export") -> str:
        """
        Xuất dữ liệu sang Google Sheets và trả về URL chia sẻ.
        """
        self._authenticate()
        
        # 1. Tạo Spreadsheet mới
        spreadsheet = {
            'properties': {
                'title': sheet_title
            }
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        self.spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # 2. Chuẩn bị dữ liệu
        header = ["Tên doanh nghiệp", "Số điện thoại", "Website", "Địa chỉ", "Đánh giá", "Số nhận xét", "Google Maps URL", "Emails", "Socials"]
        values = [header]
        
        for lead in leads:
            values.append([
                lead.name,
                lead.phone or "N/A",
                lead.website or "N/A",
                lead.address or "N/A",
                str(lead.rating),
                str(lead.reviews_count),
                lead.gmap_url,
                ", ".join(lead.emails),
                str(lead.socials)
            ])

        # 3. Ghi dữ liệu
        body = {
            'values': values
        }
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range="Sheet1!A1",
            valueInputOption="RAW", body=body).execute()

        # 4. Thiết lập quyền chia sẻ (Public View)
        permission = {
            'type': 'anyone',
            'role': 'viewer',
        }
        self.drive_service.permissions().create(fileId=self.spreadsheet_id, body=permission).execute()

        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit?usp=sharing"
