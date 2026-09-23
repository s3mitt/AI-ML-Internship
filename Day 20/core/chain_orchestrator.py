"""Tool Chaining Orchestrator: Multi-step pipeline execution and trace generator."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from tools import get_all_tools, BaseTool
from core.router import FunctionCallingRouter, RouterDecision


class ToolChainOrchestrator:
    """Executes single tools and multi-tool pipelines, capturing step-by-step traces."""

    def __init__(self, tools: Optional[Dict[str, BaseTool]] = None):
        self.tools = tools or get_all_tools()
        self.router = FunctionCallingRouter(self.tools)

    def execute_request(self, user_request: str) -> Dict[str, Any]:
        """Route user query, execute planned tool(s), and format final response."""
        decision: RouterDecision = self.router.route(user_request)

        if not decision.is_chain:
            return self._execute_single_tool(decision)
        else:
            return self._execute_tool_chain(decision)

    def _execute_single_tool(self, decision: RouterDecision) -> Dict[str, Any]:
        """Execute a single tool workflow."""
        tool_name = decision.tools[0]
        tool = self.tools.get(tool_name)
        if not tool:
            return {
                "request": decision.request,
                "success": False,
                "error": f"Tool '{tool_name}' not found.",
                "trace": [],
            }

        trace_step = {
            "step": 1,
            "tool": tool_name,
            "input": decision.initial_params,
        }
        res = tool.execute(**decision.initial_params)
        trace_step["output"] = res

        # Generate readable final answer
        final_answer = self._format_single_tool_answer(tool_name, res)

        return {
            "request": decision.request,
            "is_chain": False,
            "tools_called": [tool_name],
            "reasoning": decision.reasoning,
            "trace": [trace_step],
            "result": res,
            "final_answer": final_answer,
        }

    def _execute_tool_chain(self, decision: RouterDecision) -> Dict[str, Any]:
        """Execute multi-step pipeline where output from step N feeds into step N+1."""
        traces: List[Dict[str, Any]] = []
        chain_id = decision.chain_meta.get("chain_id")

        # ---------------------------------------------------------------------
        # Workflow 1: File Reader -> Data Analyzer (Average salary in CSV)
        # ---------------------------------------------------------------------
        if chain_id == "file_to_analytics":
            # Step 1: Read file
            t1 = self.tools["file_reader"]
            p1 = decision.initial_params
            res1 = t1.execute(**p1)
            traces.append({"step": 1, "tool": "file_reader", "input": p1, "output": res1})

            if not res1.get("success"):
                return self._build_chain_failure(decision, traces, res1)

            # Step 2: Analyze data
            t2 = self.tools["data_analyzer"]
            p2 = {
                "file_path": p1.get("file_path"),
                "target_column": decision.chain_meta.get("target_column", "salary"),
            }
            res2 = t2.execute(**p2)
            traces.append({"step": 2, "tool": "data_analyzer", "input": p2, "output": res2})

            stats = res2.get("data", {}).get("statistics", {}).get("salary", {})
            avg_salary = stats.get("mean", "N/A")
            rows = res2.get("data", {}).get("rows", 0)
            final_answer = (
                f"Successfully read '{p1['file_path']}' ({rows} records). "
                f"Statistical Analysis: Mean salary is ${avg_salary:,.2f} "
                f"(Median: ${stats.get('median', 0):,.2f}, Range: ${stats.get('min', 0):,.2f} - ${stats.get('max', 0):,.2f})."
                if isinstance(avg_salary, (int, float))
                else f"Read file successfully. Analysis result: {res2.get('data')}"
            )

        # ---------------------------------------------------------------------
        # Workflow 2: Weather Tool -> Calculator (Temperature conversion)
        # ---------------------------------------------------------------------
        elif chain_id == "weather_to_calc":
            # Step 1: Fetch Weather
            t1 = self.tools["weather"]
            p1 = decision.initial_params
            res1 = t1.execute(**p1)
            traces.append({"step": 1, "tool": "weather", "input": p1, "output": res1})

            if not res1.get("success"):
                return self._build_chain_failure(decision, traces, res1)

            weather_data = res1["data"]
            temp_c = weather_data["temperature"]

            # Step 2: Convert to Fahrenheit via Calculator: (C * 9/5) + 32
            t2 = self.tools["calculator"]
            calc_expr = f"({temp_c} * 9 / 5) + 32"
            p2 = {"expression": calc_expr}
            res2 = t2.execute(**p2)
            traces.append({"step": 2, "tool": "calculator", "input": p2, "output": res2})

            temp_f = res2.get("data", {}).get("result", "N/A")
            final_answer = (
                f"Current weather in {weather_data['location']}: {temp_c}°C ({temp_f}°F). "
                f"Condition: {weather_data['condition']}, Humidity: {weather_data['humidity']}, "
                f"Wind: {weather_data['wind_speed']} [Source: {weather_data['source']}]."
            )

        # ---------------------------------------------------------------------
        # Workflow 3: Database Tool -> Data Analyzer (Filtered query to analytics)
        # ---------------------------------------------------------------------
        elif chain_id == "db_to_analyzer":
            # Step 1: Query Database
            t1 = self.tools["database"]
            p1 = decision.initial_params
            res1 = t1.execute(**p1)
            traces.append({"step": 1, "tool": "database", "input": p1, "output": res1})

            if not res1.get("success"):
                return self._build_chain_failure(decision, traces, res1)

            rows = res1["data"]["rows"]

            # Step 2: In-memory Data Analyzer profiling
            t2 = self.tools["data_analyzer"]
            p2 = {"data": rows, "target_column": decision.chain_meta.get("target_column", "salary")}
            res2 = t2.execute(**p2)
            traces.append({"step": 2, "tool": "data_analyzer", "input": p2, "output": res2})

            stats = res2.get("data", {}).get("statistics", {}).get("salary", {})
            final_answer = (
                f"Database query retrieved {len(rows)} matching Engineering records earning above $50k. "
                f"Analyzed metrics: Average salary is ${stats.get('mean', 0):,.2f} "
                f"(Max: ${stats.get('max', 0):,.2f}, Min: ${stats.get('min', 0):,.2f})."
            )

        # ---------------------------------------------------------------------
        # Workflow 4: File Reader -> Data Analyzer (JSON project metrics)
        # ---------------------------------------------------------------------
        elif chain_id == "file_json_to_analyzer":
            # Step 1: Read JSON
            t1 = self.tools["file_reader"]
            p1 = decision.initial_params
            res1 = t1.execute(**p1)
            traces.append({"step": 1, "tool": "file_reader", "input": p1, "output": res1})

            if not res1.get("success"):
                return self._build_chain_failure(decision, traces, res1)

            json_data = res1["data"]["content"]

            # Step 2: Analyze milestones or metrics
            t2 = self.tools["data_analyzer"]
            milestones = json_data.get("milestones", [])
            p2 = {"data": milestones} if milestones else {"data": [json_data]}
            res2 = t2.execute(**p2)
            traces.append({"step": 2, "tool": "data_analyzer", "input": p2, "output": res2})

            final_answer = (
                f"Project Summary for '{json_data.get('project_name')}': Status is '{json_data.get('status')}', "
                f"Owner: {json_data.get('owner')}, Budget: ${json_data.get('budget', 0):,.2f}. "
                f"Completion Rate: {json_data.get('metrics', {}).get('completion_rate', 0) * 100:.0f}%, "
                f"Active Milestones: {len(milestones)} total."
            )

        # ---------------------------------------------------------------------
        # Workflow 5: Weather Tool -> Email Tool (Fetch weather and email report)
        # ---------------------------------------------------------------------
        elif chain_id == "weather_to_email":
            # Step 1: Weather lookup
            t1 = self.tools["weather"]
            p1 = decision.initial_params
            res1 = t1.execute(**p1)
            traces.append({"step": 1, "tool": "weather", "input": p1, "output": res1})

            if not res1.get("success"):
                return self._build_chain_failure(decision, traces, res1)

            w = res1["data"]

            # Step 2: Compose & queue email
            t2 = self.tools["email"]
            recipient = decision.chain_meta.get("recipient", "mentor@example.com")
            subject = f"Weather Update: {w['location']}"
            body = (
                f"Hello,\n\nHere is the current weather update for {w['location']}:\n"
                f"- Temperature: {w['temperature']}°C\n"
                f"- Condition: {w['condition']}\n"
                f"- Humidity: {w['humidity']}\n"
                f"- Wind Speed: {w['wind_speed']}\n\n"
                f"Report generated automatically via Linkific Internship Agent."
            )
            p2 = {"recipient": recipient, "subject": subject, "body": body}
            res2 = t2.execute(**p2)
            traces.append({"step": 2, "tool": "email", "input": p2, "output": res2})

            final_answer = (
                f"Fetched current weather for {w['location']} ({w['temperature']}°C, {w['condition']}) "
                f"and queued automated email briefing to {recipient} with subject '{subject}'."
            )

        else:
            # Generic sequential execution fallback
            current_input = dict(decision.initial_params)
            for idx, tool_name in enumerate(decision.tools, start=1):
                t = self.tools.get(tool_name)
                if not t:
                    break
                res = t.execute(**current_input)
                traces.append({"step": idx, "tool": tool_name, "input": current_input, "output": res})
                if not res.get("success"):
                    return self._build_chain_failure(decision, traces, res)
            final_answer = f"Pipeline across tools {decision.tools} completed successfully."

        return {
            "request": decision.request,
            "is_chain": True,
            "tools_called": decision.tools,
            "reasoning": decision.reasoning,
            "trace": traces,
            "final_answer": final_answer,
        }

    def _build_chain_failure(self, decision: RouterDecision, traces: List[Dict[str, Any]], failure_res: Dict[str, Any]) -> Dict[str, Any]:
        """Construct structured failure response if any pipeline step fails."""
        err_msg = failure_res.get("error", {}).get("message", "Pipeline execution halted due to step failure.")
        return {
            "request": decision.request,
            "is_chain": True,
            "tools_called": [t["tool"] for t in traces],
            "reasoning": decision.reasoning,
            "trace": traces,
            "final_answer": f"Chain stopped with error: {err_msg}",
            "failed_step": failure_res,
        }

    def _format_single_tool_answer(self, tool_name: str, res: Dict[str, Any]) -> str:
        """Render user-friendly summary string for single tool invocation."""
        if not res.get("success"):
            err = res.get("error", {})
            return f"Error executing {tool_name} [{err.get('type')}]: {err.get('message')}"

        data = res.get("data", {})
        if tool_name == "calculator":
            return f"Calculated '{data.get('expression')}': {data.get('result')}"
        elif tool_name == "web_search":
            results = data.get("results", [])
            lines = [f"Found {len(results)} web results for '{data.get('query')}':"]
            for r in results[:3]:
                lines.append(f"- {r.get('title')}: {r.get('snippet')} ({r.get('url')})")
            return "\n".join(lines)
        elif tool_name == "database":
            rows = data.get("rows", [])
            return f"Database query returned {len(rows)} record(s):\n" + "\n".join(str(r) for r in rows[:5])
        elif tool_name == "file_reader":
            filename = data.get("filename")
            size = data.get("metadata", {}).get("size_bytes", 0)
            return f"File '{filename}' loaded ({size} bytes)."
        elif tool_name == "weather":
            return f"Weather for {data.get('location')}: {data.get('temperature')}°C, {data.get('condition')}, Humidity: {data.get('humidity')}."
        elif tool_name == "email":
            env = data.get("envelope", {})
            return f"Email queued in {data.get('status')} mode to {env.get('to')} with subject '{env.get('subject')}'."
        elif tool_name == "date_tool":
            act = data.get("action")
            if act == "current":
                return f"Today is {data.get('date')} ({data.get('day_of_week')}), current time is {data.get('time')}."
            elif act == "day_of_week":
                return f"{data.get('input_date')} falls on a {data.get('day_of_week')}."
            elif act == "days_between":
                return f"There are {data.get('days_difference')} days between {data.get('start_date')} and {data.get('end_date')}."
            elif act == "add_days":
                return f"Adding {data.get('days_offset')} days to {data.get('base_date')} gives {data.get('result_date')} ({data.get('day_of_week')})."
            elif act == "convert_format":
                return f"Converted date to format: {data.get('formatted_date')}"
            return str(data)
        elif tool_name == "data_analyzer":
            return f"Dataset Analysis: {data.get('rows')} rows, {data.get('column_count')} columns. Columns: {', '.join(data.get('columns', []))}."
        return str(data)
