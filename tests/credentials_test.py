from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import config

def get_google_sheets_service():
    """Returns an authenticated Google Sheets service client."""
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE)
    return build("sheets", "v4", credentials=creds)

def read_google_sheet():
    """Reads data from a Google Sheet."""
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.SHEET_ID, range="Sheet1!A1:H").execute()
    return result.get("values", [])

if __name__ == "__main__":
    data = read_google_sheet()
    print(data)
