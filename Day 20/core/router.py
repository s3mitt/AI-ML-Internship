"""Function Calling Router: Rule-based local router & LLM function-calling schema exporter."""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from tools import get_all_tools, BaseTool


class RouterDecision:
    """Represents a routing decision containing the tool or chain to execute and initial parameters."""

    def __init__(
        self,
        request: str,
        is_chain: bool,
        tools: List[str],
        reasoning: str,
        initial_params: Dict[str, Any],
        chain_meta: Optional[Dict[str, Any]] = None,
    ):
        self.request = request
        self.is_chain = is_chain
        self.tools = tools
        self.reasoning = reasoning
        self.initial_params = initial_params
        self.chain_meta = chain_meta or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request,
            "is_chain": self.is_chain,
            "tools": self.tools,
            "reasoning": self.reasoning,
            "initial_params": self.initial_params,
            "chain_meta": self.chain_meta,
        }


class FunctionCallingRouter:
    """Routes user queries to single tools or multi-tool pipelines."""

    def __init__(self, registered_tools: Optional[Dict[str, BaseTool]] = None):
        self.tools = registered_tools or get_all_tools()

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Export all registered tools in OpenAI/Gemini function calling schema format."""
        return [tool.to_function_schema() for tool in self.tools.values()]

    def route(self, user_request: str) -> RouterDecision:
        """Analyze intent from user prompt and return routing decision."""
        req = user_request.strip()
        lower_req = req.lower()

        # ---------------------------------------------------------------------
        # 1. TOOL CHAINING INTENT DETECTION (Multi-step workflows)
        # ---------------------------------------------------------------------

        # Chain 1: Read CSV/file + calculate average/stats
        if ("read" in lower_req or "open" in lower_req) and ("csv" in lower_req or "file" in lower_req) and ("average" in lower_req or "salary" in lower_req or "mean" in lower_req):
            match = re.search(r"([a-zA-Z0-9_\-\./]+\.csv)", req, re.IGNORECASE)
            file_path = match.group(1) if match else "data/employees.csv"
            return RouterDecision(
                request=req,
                is_chain=True,
                tools=["file_reader", "data_analyzer"],
                reasoning="Request requires reading tabular employee file first, followed by statistical aggregation of salary.",
                initial_params={"file_path": file_path},
                chain_meta={"chain_id": "file_to_analytics", "target_column": "salary"},
            )

        # Chain 2: Weather + Convert to Fahrenheit / Math
        if ("weather" in lower_req or "temperature" in lower_req) and ("fahrenheit" in lower_req or "convert" in lower_req or "calc" in lower_req):
            match = re.search(r"in\s+([a-zA-Z\s]+?)(?:\s+and|\s+convert|\?|$)", req, re.IGNORECASE)
            city = match.group(1).strip() if match else "Kolkata"
            return RouterDecision(
                request=req,
                is_chain=True,
                tools=["weather", "calculator"],
                reasoning="Requires fetching real-time Celsius temperature from weather service, then passing the value to calculator for Fahrenheit conversion.",
                initial_params={"location": city},
                chain_meta={"chain_id": "weather_to_calc", "conversion": "celsius_to_fahrenheit"},
            )

        # Chain 3: Database query + analyze average/distribution
        if ("database" in lower_req or "db" in lower_req or "engineering" in lower_req or "select" in lower_req) and ("average" in lower_req or "salary" in lower_req or "calculate" in lower_req or "analyze" in lower_req):
            return RouterDecision(
                request=req,
                is_chain=True,
                tools=["database", "data_analyzer"],
                reasoning="Requires querying employee records filtered by department/salary from SQLite, then passing structured rows to data analyzer.",
                initial_params={
                    "query": "SELECT * FROM employees WHERE department = ? AND salary > ?",
                    "parameters": ["Engineering", 50000],
                },
                chain_meta={"chain_id": "db_to_analyzer", "target_column": "salary"},
            )

        # Chain 4: Read JSON project status + summarize / analyze
        if ("read" in lower_req or "status" in lower_req) and ("json" in lower_req or "project" in lower_req) and ("summary" in lower_req or "prepare" in lower_req or "metrics" in lower_req):
            match = re.search(r"([a-zA-Z0-9_\-\./]+\.json)", req, re.IGNORECASE)
            file_path = match.group(1) if match else "data/sample.json"
            return RouterDecision(
                request=req,
                is_chain=True,
                tools=["file_reader", "data_analyzer"],
                reasoning="Requires extracting structured JSON configuration from storage, followed by extracting milestone/metrics telemetry.",
                initial_params={"file_path": file_path},
                chain_meta={"chain_id": "file_json_to_analyzer"},
            )

        # Chain 5: Weather + send email
        if ("weather" in lower_req or "forecast" in lower_req) and ("email" in lower_req or "send" in lower_req or "mail" in lower_req):
            match_city = re.search(r"(?:weather\s+(?:in|for)|city)\s+([a-zA-Z\s]+?)(?:\s+and|\s+email|\?|$)", req, re.IGNORECASE)
            city = match_city.group(1).strip() if match_city else "Kolkata"
            match_email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", req)
            recipient = match_email.group(1) if match_email else "mentor@example.com"
            return RouterDecision(
                request=req,
                is_chain=True,
                tools=["weather", "email"],
                reasoning="Requires fetching local weather metrics, then composing and dispatching a formatted email summary to the recipient.",
                initial_params={"location": city},
                chain_meta={"chain_id": "weather_to_email", "recipient": recipient},
            )

        # ---------------------------------------------------------------------
        # 2. SINGLE TOOL INTENT ROUTING
        # ---------------------------------------------------------------------

        # Email Tool
        if "email" in lower_req or "send an email" in lower_req or "mail to" in lower_req:
            match_email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", req)
            recipient = match_email.group(1) if match_email else "mentor@example.com"
            match_sub = re.search(r"subject\s+([^\.]+?)(?:\s+and|\s+body|\.|$)", req, re.IGNORECASE)
            subject = match_sub.group(1).strip() if match_sub else "Internship Update"
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["email"],
                reasoning="User explicitly intends to draft or transmit an email message.",
                initial_params={
                    "recipient": recipient,
                    "subject": subject,
                    "body": "Here is today's internship progress update detailing tool creation and chaining.",
                },
            )

        # Date Tool
        if any(w in lower_req for w in ["date", "today", "day is", "days between", "days from today", "calendar", "weekday"]):
            action = "current"
            params: Dict[str, Any] = {"action": action}
            if "days from today" in lower_req or "days to" in lower_req or "after" in lower_req or "from today" in lower_req:
                match_days = re.search(r"(\d+)\s+days", lower_req)
                days_val = int(match_days.group(1)) if match_days else 30
                params = {"action": "add_days", "days": days_val}
            elif "days between" in lower_req:
                params = {"action": "days_between", "start_date": "2026-09-01", "end_date": "2026-09-25"}
            elif "what day is" in lower_req or "day of week" in lower_req:
                match_dt = re.search(r"(?:what day is|day of week for)\s+(.+?)(?:\?|$)", req, re.IGNORECASE)
                dt_str = match_dt.group(1).strip() if match_dt else "25 September 2026"
                params = {"action": "day_of_week", "date": dt_str}

            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["date_tool"],
                reasoning="Request asks for temporal, calendar, or date arithmetic operations.",
                initial_params=params,
            )

        # Weather Tool
        if "weather" in lower_req or "temperature in" in lower_req:
            match = re.search(r"(?:in|for)\s+([a-zA-Z\s]+?)(?:\?|$)", req, re.IGNORECASE)
            city = match.group(1).strip() if match else "Kolkata"
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["weather"],
                reasoning="User is querying meteorological conditions for a specific location.",
                initial_params={"location": city},
            )

        # Database Tool
        if any(w in lower_req for w in ["database", "employees earning", "engineering employees", "employees in", "count employees"]):
            if "engineering" in lower_req and ("50000" in lower_req or "above" in lower_req):
                params = {
                    "query": "SELECT * FROM employees WHERE department = ? AND salary > ?",
                    "parameters": ["Engineering", 50000],
                }
            elif "count" in lower_req and "department" in lower_req:
                params = {
                    "query": "SELECT department, COUNT(*) as count FROM employees GROUP BY department",
                    "parameters": [],
                }
            elif "engineering" in lower_req:
                params = {
                    "query": "SELECT * FROM employees WHERE department = ?",
                    "parameters": ["Engineering"],
                }
            else:
                params = {
                    "query": "SELECT * FROM employees LIMIT 5",
                    "parameters": [],
                }
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["database"],
                reasoning="Request specifies querying relational tabular entity data from SQLite.",
                initial_params=params,
            )

        # File Reader
        if lower_req.startswith("read") or lower_req.startswith("extract") or "internship_notes" in lower_req or "readme" in lower_req:
            match = re.search(r"([a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)", req)
            target_file = match.group(1) if match else "data/internship_notes.md"
            if not target_file.startswith("data/"):
                target_file = f"data/{target_file}"
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["file_reader"],
                reasoning="User requests inspection or reading of local repository file contents.",
                initial_params={"file_path": target_file},
            )

        # Data Analyzer
        if lower_req.startswith("analyze") or "statistics" in lower_req or "dataset" in lower_req:
            match = re.search(r"([a-zA-Z0-9_\-\./]+\.(?:csv|json))", req)
            target_file = match.group(1) if match else "data/employees.csv"
            if not target_file.startswith("data/"):
                target_file = f"data/{target_file}"
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["data_analyzer"],
                reasoning="Request specifies structural, statistical, or grouping analysis on tabular data.",
                initial_params={"file_path": target_file},
            )

        # Calculator
        math_symbols = {"+", "*", "/", "%", "^", "calculate", "average"}
        if any(sym in lower_req for sym in math_symbols) or re.search(r"\d+\s*[\+\-\*\/]\s*\d+", req):
            expr = re.sub(r"(?i)^calculate\s+", "", req).strip().rstrip("?").strip()
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["calculator"],
                reasoning="Request contains mathematical expressions, percentages, or numeric averages.",
                initial_params={"expression": expr},
            )

        # Web Search (Default for general search, latest info, queries)
        if any(w in lower_req for w in ["search", "latest", "google", "find online", "news", "articles"]):
            q = re.sub(r"(?i)^(?:search\s+(?:the\s+web\s+for|for)?|find\s+online)\s*", "", req).strip()
            return RouterDecision(
                request=req,
                is_chain=False,
                tools=["web_search"],
                reasoning="Request seeks real-time, external, or online information across the web.",
                initial_params={"query": q or req},
            )

        # Fallback to Web Search
        return RouterDecision(
            request=req,
            is_chain=False,
            tools=["web_search"],
            reasoning="Broad informational query routed to Web Search engine.",
            initial_params={"query": req},
        )
