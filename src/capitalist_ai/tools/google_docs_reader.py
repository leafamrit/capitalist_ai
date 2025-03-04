from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

class GoogleDocReaderInput(BaseModel):
    """Input schema for GoogleDocReader."""
    doc_url: str = Field(..., description="URL of the Google Doc to read")

class GoogleDocReader(BaseTool):
    name: str = "Google Doc Reader"
    description: str = (
        "A tool that reads content from a Google Doc. "
        "Provide the Google Doc URL and it will return the document's content."
    )
    args_schema: Type[BaseModel] = GoogleDocReaderInput

    def _extract_doc_id(self, doc_url: str) -> str:
        """Extract the document ID from a Google Docs URL."""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', doc_url)
        if not match:
            raise ValueError("Invalid Google Docs URL format")
        return match.group(1)

    def _get_credentials(self):
        """Get Google API credentials from service account."""
        try:
            return service_account.Credentials.from_service_account_file(
                'cmdandfn-gcpkey.json',
                scopes=['https://www.googleapis.com/auth/documents.readonly']
            )
        except Exception as e:
            raise Exception(f"Failed to load credentials: {str(e)}")

    def _extract_text(self, doc_id: str, credentials) -> str:
        """Extract text content from the Google Doc."""
        try:
            service = build('docs', 'v1', credentials=credentials)
            document = service.documents().get(documentId=doc_id).execute()
            content = []
            
            for element in document.get('body').get('content'):
                if 'paragraph' in element:
                    for para_element in element.get('paragraph').get('elements'):
                        if 'textRun' in para_element:
                            content.append(para_element.get('textRun').get('content'))
            
            return '\n'.join(content)
        except Exception as e:
            raise Exception(f"Failed to extract document content: {str(e)}")

    def _run(self, doc_url: str) -> str:
        """Read the Google Doc content."""
        try:
            # Extract document ID
            doc_id = self._extract_doc_id(doc_url)
            
            # Get credentials
            credentials = self._get_credentials()
            
            # Extract and return text content
            return self._extract_text(doc_id, credentials)
            
        except Exception as e:
            return f"Failed to read document: {str(e)}"
