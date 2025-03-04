from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

class GoogleSheetsReaderInput(BaseModel):
    """Input schema for GoogleSheetsReader."""
    sheet_url: str = Field(..., description="URL of the Google Sheet to read")
    range: str = Field(default="A1:Z1000", description="Range to read (e.g., 'Sheet1!A1:Z10')")

class GoogleSheetsReader(BaseTool):
    name: str = "Google Sheets Reader"
    description: str = (
        "A tool that reads content from a Google Sheet. "
        "Provide the Google Sheet URL and optionally a range to read specific cells. "
        "Returns the sheet's content in a structured format."
    )
    args_schema: Type[BaseModel] = GoogleSheetsReaderInput

    def _extract_sheet_id(self, sheet_url: str) -> str:
        """Extract the spreadsheet ID from a Google Sheets URL."""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            raise ValueError("Invalid Google Sheets URL format")
        return match.group(1)

    def _get_credentials(self):
        """Get Google API credentials from service account."""
        try:
            return service_account.Credentials.from_service_account_file(
                'cmdandfn-gcpkey.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        except Exception as e:
            raise Exception(f"Failed to load credentials: {str(e)}")

    def _extract_data(self, sheet_id: str, range: str, credentials) -> str:
        """Extract data from the Google Sheet."""
        try:
            service = build('sheets', 'v4', credentials=credentials)
            sheet = service.spreadsheets()
            
            # Get the sheet data
            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range=range
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return "No data found in the specified range."
            
            # Format the data as a readable string
            formatted_data = []
            for row in values:
                formatted_data.append('\t'.join(str(cell) for cell in row))
            
            return '\n'.join(formatted_data)
            
        except Exception as e:
            raise Exception(f"Failed to extract sheet data: {str(e)}")

    def _run(self, sheet_url: str, range: str = "A1:Z1000") -> str:
        """Read the Google Sheet content."""
        try:
            # Extract spreadsheet ID
            sheet_id = self._extract_sheet_id(sheet_url)
            
            # Get credentials
            credentials = self._get_credentials()
            
            # Extract and return sheet data
            return self._extract_data(sheet_id, range, credentials)
            
        except Exception as e:
            return f"Failed to read spreadsheet: {str(e)}"
