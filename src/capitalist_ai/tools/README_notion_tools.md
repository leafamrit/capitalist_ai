# Notion Tools for Capitalist AI

This module provides tools for interacting with Notion databases and pages. It allows agents to:

1. Query Notion databases and retrieve their contents
2. Read the content of specific Notion pages
3. Query databases and include the full content of each page

## Setup

### 1. Install Dependencies

The Notion tools require the `notion-client` package:

```bash
pip install notion-client
```

### 2. Obtain a Notion API Key

To use these tools, you need a Notion API key:

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give your integration a name and select the workspace where you want to use it
4. Click "Submit" to create the integration
5. Copy the "Internal Integration Token" - this is your API key

### 3. Share Databases and Pages with Your Integration

For your integration to access a database or page, you need to share it with the integration:

1. Open the Notion database or page you want to access
2. Click the "Share" button in the top right
3. In the "Add people, groups, or integrations" field, select your integration
4. Click "Invite"

## Usage

### Basic Usage

```python
from capitalist_ai.tools import NotionDatabaseReader, NotionPageReader

# Initialize the tools with your API key
notion_api_key = "your_notion_api_key"
database_reader = NotionDatabaseReader(api_key=notion_api_key)
page_reader = NotionPageReader(api_key=notion_api_key)

# Query a Notion database
database_results = database_reader._run(
    database_id_or_url="your_database_id_or_url",
    max_pages=10
)

# Read a Notion page
page_content = page_reader._run(
    page_id_or_url="your_page_id_or_url"
)
```

### Advanced Usage

#### Filtering Database Results

```python
# Query a database with a filter
filtered_results = database_reader._run(
    database_id_or_url="your_database_id_or_url",
    filter_property="Status",  # Replace with an actual property name in your database
    filter_value="Completed",  # Replace with a value to filter by
    max_pages=10
)
```

#### Including Page Content in Database Results

```python
# Query a database and include the full content of each page
database_with_content = database_reader._run(
    database_id_or_url="your_database_id_or_url",
    max_pages=5,
    include_page_content=True
)
```

## Integration with CrewAI

These tools are designed to work with CrewAI. Here's how to use them in a CrewAI agent:

```python
from crewai import Agent, Task, Crew
from capitalist_ai.tools import NotionDatabaseReader, NotionPageReader

# Initialize the tools
notion_api_key = "your_notion_api_key"
database_reader = NotionDatabaseReader(api_key=notion_api_key)
page_reader = NotionPageReader(api_key=notion_api_key)

# Create an agent with the Notion tools
researcher = Agent(
    role="Researcher",
    goal="Research information from Notion databases",
    backstory="You are a skilled researcher who analyzes data from Notion databases.",
    tools=[database_reader, page_reader]
)

# Create a task that uses the Notion tools
research_task = Task(
    description=(
        "Research information from the Notion database at 'your_database_id_or_url'. "
        "Analyze the data and provide insights."
    ),
    agent=researcher
)

# Create and run the crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task]
)

result = crew.kickoff()
```

## Tool Details

### NotionDatabaseReader

This tool queries a Notion database and returns its contents.

**Parameters:**

- `database_id_or_url` (required): ID or URL of the Notion database to query
- `filter_property` (optional): Property name to filter by
- `filter_value` (optional): Value to filter by
- `max_pages` (optional, default=10): Maximum number of pages to retrieve
- `include_page_content` (optional, default=False): Whether to include the full content of each page

### NotionPageReader

This tool reads the content of a specific Notion page.

**Parameters:**

- `page_id_or_url` (required): ID or URL of the Notion page to read

## Output Format

Both tools return formatted text that can be easily read and processed by agents.

### Database Output Example

```
Page: Project Alpha (ID: 123456789abcdef123456789abcdef)
  Name: Project Alpha
  Status: In Progress
  Priority: High
  Due Date: 2023-12-31
  Assigned To: John Doe

Page: Project Beta (ID: abcdef123456789abcdef123456789)
  Name: Project Beta
  Status: Completed
  Priority: Medium
  Due Date: 2023-11-15
  Assigned To: Jane Smith
```

### Page Output Example

```
# Meeting Notes: Q4 Planning

## Agenda
• Review Q3 results
• Discuss Q4 goals
• Assign responsibilities

## Action Items
1. John to prepare Q3 report by Friday
2. Jane to draft Q4 goals document
3. Team to review and provide feedback by next Monday

## Notes
This meeting is critical for our year-end planning. Please come prepared with your department's metrics and proposed goals for Q4.
```

## Limitations

- The current implementation uses a simplified filter mechanism that works best with text properties. For more complex filtering, you may need to extend the `_build_filter` method.
- For pages with nested blocks (blocks that have children), the tool indicates that children exist but doesn't retrieve their content. This is a simplification to avoid excessive API calls.
- Some complex block types (like tables) are represented in a simplified form.
