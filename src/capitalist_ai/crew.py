from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool
from .tools.google_docs_reader import GoogleDocReader
from .tools.google_sheets_reader import GoogleSheetsReader
from .tools.mongodb_helper import MongoDBHelper
from functools import wraps

@CrewBase
class CapitalistAI():
    """CapitalistAI crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, crew_inputs):
        """Initialize CapitalistAI with lazy-loaded tools."""
        self.google_doc_reader = None
        self.google_sheets_reader = None
        self.serper_dev_tool = None
        self.mongodb_helper = MongoDBHelper()
        self.pricing_websearch_tool = WebsiteSearchTool(
            website=crew_inputs["pricing"]
        )
        self.pricing_webscrape_tool = ScrapeWebsiteTool(
            website_url=crew_inputs["pricing"]
        )
        self.website_websearch_tool = WebsiteSearchTool(
            website=crew_inputs["website"]
        )
        self.website_webscrape_tool = ScrapeWebsiteTool(
            website_url=crew_inputs["website"]
        )
        self.productbacklog_websearch_tool = WebsiteSearchTool(
            website=crew_inputs["productbacklog"]
        )
        self.productbacklog_webscrape_tool = ScrapeWebsiteTool(
            website_url=crew_inputs["productbacklog"]
        )

    def _init_tools(self):
        """Initialize tools if they haven't been initialized yet."""
        if self.google_doc_reader is None:
            self.google_doc_reader = GoogleDocReader()
        if self.google_sheets_reader is None:
            self.google_sheets_reader = GoogleSheetsReader()
        if self.serper_dev_tool is None:
            self.serper_dev_tool = SerperDevTool()

    @agent
    def mrb(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['mrb'],
            verbose=False,
            allow_delegation=False,
            tools=[self.serper_dev_tool, self.website_webscrape_tool, self.website_websearch_tool]
        )

    @agent
    def mab(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['mab'],
            verbose=False,
            tools=[self.google_doc_reader, self.google_sheets_reader, self.website_webscrape_tool, self.website_websearch_tool, self.pricing_webscrape_tool, self.pricing_websearch_tool]
        )
    
    @agent
    def csb(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['csb'],
            verbose=False,
            allow_delegation=True,
            tools=[self.google_doc_reader, self.google_sheets_reader, self.website_webscrape_tool, self.website_websearch_tool]
        )
    
    @agent
    def fsb(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['fsb'],
            verbose=False,
            allow_delegation=True,
            tools=[self.google_doc_reader, self.google_sheets_reader, self.website_webscrape_tool, self.website_websearch_tool, self.productbacklog_webscrape_tool, self.productbacklog_websearch_tool]
        )
    
    @agent
    def rcb(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['rcb'],
            verbose=False,
            tools=[self.website_webscrape_tool, self.website_websearch_tool]
        )
    
    @agent
    def pmb(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['pmb'],
            verbose=False,
            tools=[self.google_doc_reader, self.google_sheets_reader, self.serper_dev_tool, self.website_webscrape_tool, self.website_websearch_tool]
        )

    @agent
    def qab(self) -> Agent:
        self._init_tools()
        return Agent(
            config=self.agents_config['qab'],
            verbose=False,
            tools=[self.google_doc_reader, self.google_sheets_reader]
        )

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_research_task'],
        )

    @task
    def metrics_analyzer_task(self) -> Task:
        return Task(
            config=self.tasks_config['metrics_analyzer_task'],
        )
    
    @task
    def chief_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['chief_strategy_task'],
        )
    
    @task
    def feature_scoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['feature_scoring_task'],
        )
    
    @task
    def reality_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['reality_check_task'],
        )
    
    @task
    def final_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_summary_task'],
        )
    
    @task
    def quality_assurance_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_assurance_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CapitalistAI crew"""
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )

        return crew
