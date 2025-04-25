"""
Example script demonstrating how to use the Notion Database Reader and Page Reader tools.

This script shows how to:
1. Query a Notion database and retrieve its contents
2. Read the content of a specific Notion page
3. Query a database and include the full content of each page

To use this script:
1. Replace the dummy API key with your actual Notion API key
2. Replace the database_id and page_id with your actual Notion database and page IDs
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the tools
sys.path.append(str(Path(__file__).parent.parent.parent))

from capitalist_ai.tools import NotionDatabaseReader, NotionPageReader

def main():
    # Replace this with your actual Notion API key
    notion_api_key = os.environ.get("NOTION_API_KEY", "secret_dummy_notion_api_key")
    
    # Initialize the tools with your API key
    database_reader = NotionDatabaseReader(api_key=notion_api_key)
    page_reader = NotionPageReader(api_key=notion_api_key)
    
    # Example 1: Query a Notion database
    print("\n=== Example 1: Query a Notion database ===\n")
    
    # Replace with your actual database ID or URL
    database_id = "your_database_id_or_url"
    
    # Query the database (up to 5 pages)
    database_results = database_reader._run(
        database_id_or_url=database_id,
        max_pages=5
    )
    
    print(database_results)
    
    # Example 2: Read a specific Notion page
    print("\n=== Example 2: Read a specific Notion page ===\n")
    
    # Replace with your actual page ID or URL
    page_id = "your_page_id_or_url"
    
    # Read the page content
    page_content = page_reader._run(
        page_id_or_url=page_id
    )
    
    print(page_content)
    
    # Example 3: Query a database and include page content
    print("\n=== Example 3: Query a database with page content ===\n")
    
    # Query the database and include page content (up to 2 pages)
    database_with_content = database_reader._run(
        database_id_or_url=database_id,
        max_pages=2,
        include_page_content=True
    )
    
    print(database_with_content)
    
    # Example 4: Filter database results
    print("\n=== Example 4: Filter database results ===\n")
    
    # Query the database with a filter
    filtered_results = database_reader._run(
        database_id_or_url=database_id,
        filter_property="Status",  # Replace with an actual property name in your database
        filter_value="Completed",  # Replace with a value to filter by
        max_pages=5
    )
    
    print(filtered_results)

if __name__ == "__main__":
    main()
