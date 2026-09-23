"""Tools module registering all available agent tools."""

from typing import Dict
from tools.base import BaseTool
from tools.calculator import CalculatorTool
from tools.web_search import WebSearchTool
from tools.database import DatabaseTool
from tools.file_reader import FileReaderTool
from tools.weather import WeatherTool
from tools.email_tool import EmailTool
from tools.date_tool import DateTool
from tools.data_analyzer import DataAnalyzerTool

__all__ = [
    "BaseTool",
    "CalculatorTool",
    "WebSearchTool",
    "DatabaseTool",
    "FileReaderTool",
    "WeatherTool",
    "EmailTool",
    "DateTool",
    "DataAnalyzerTool",
    "get_all_tools",
]


def get_all_tools() -> Dict[str, BaseTool]:
    """Instantiate and return dictionary of all registered tools."""
    tools = [
        CalculatorTool(),
        WebSearchTool(),
        DatabaseTool(),
        FileReaderTool(),
        WeatherTool(),
        EmailTool(),
        DateTool(),
        DataAnalyzerTool(),
    ]
    return {tool.name: tool for tool in tools}
