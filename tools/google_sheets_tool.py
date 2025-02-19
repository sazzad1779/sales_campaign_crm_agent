from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import config as settings

class GoogleSheetsTool:
    def __init__(self):
        """Initialize Google Sheets API client"""
        creds = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_FILE)
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

    def read_leads(self, range="Sheet1!A2:H"):
        """Fetch lead data from Google Sheets."""
        result = self.sheet.values().get(spreadsheetId=settings.SHEET_ID, range=range).execute()
        return result.get("values", [])

    def update_lead(self, row, col, value):
        """Update a specific lead field in Google Sheets."""
        range_ = f"Sheet1!{col}{row}"
        body = {"values": [[value]]}
        self.sheet.values().update(
            spreadsheetId=settings.SHEET_ID,
            range=range_,
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"Updated row {row}, column {col} with '{value}'")
