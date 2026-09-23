"""Main CLI Application for Day 20: Function Calling, Tool Chaining & Error Handling."""

from __future__ import annotations
import argparse
import json
import sys
from typing import List
from core.chain_orchestrator import ToolChainOrchestrator
from tools.database import init_database

DEMO_QUERIES: List[str] = [
    "Calculate 45 * 23",
    "What's the weather in Kolkata?",
    "Search the web for the latest AI news.",
    "Read internship_notes.md",
    "Find Engineering employees earning above 50000.",
    "What date will it be 45 days from today?",
    "Analyze employees.csv.",
    "Send an email to my mentor with today's internship update.",
    "Read employees.csv and calculate the average salary.",
    "Get the weather in Kolkata and convert the temperature to Fahrenheit.",
    "Find all Engineering employees from the database and calculate their average salary.",
    "Read the project status from sample.json and prepare a summary.",
]


def print_banner() -> None:
    print("=" * 78)
    print("   LINKIFIC INTERNSHIP - DAY 20: FUNCTION CALLING & TOOL CHAINING ENGINE   ")
    print("=" * 78)
    print("Available Tools: Calculator, Web Search, Database, File Reader, Weather,")
    print("                 Email, Date Tool, Data Analyzer.")
    print("Modes: Interactive Prompt (type 'exit' to quit) | Automated Demo (--demo)")
    print("-" * 78)


def display_execution(result: dict) -> None:
    print("\n" + "-" * 60)
    print(f"Request:   {result['request']}")
    print(f"Workflow:  {'Multi-Tool Chain' if result.get('is_chain') else 'Single Tool'}")
    print(f"Tools:     {' -> '.join(result.get('tools_called', []))}")
    print(f"Reasoning: {result.get('reasoning')}")
    print("-" * 60)

    print("Execution Trace:")
    for step in result.get("trace", []):
        tool_name = step.get("tool")
        step_num = step.get("step")
        inputs = json.dumps(step.get("input"), indent=2)
        print(f"  [Step {step_num}] Tool: {tool_name}")
        print(f"    Input:  {inputs}")
        output = step.get("output")
        if output:
            success = output.get("success")
            status_str = "SUCCESS" if success else "FAILED"
            print(f"    Status: {status_str}")
            if not success:
                print(f"    Error:  {output.get('error')}")

    print("\nFinal Response:")
    print(f"  {result.get('final_answer')}")
    print("-" * 60)


def run_demo() -> None:
    print("\n>>> Running Automated Verification Demo (12 Queries) <<<\n")
    orchestrator = ToolChainOrchestrator()
    for idx, query in enumerate(DEMO_QUERIES, start=1):
        print(f"\n[Test Query #{idx}] '{query}'")
        res = orchestrator.execute_request(query)
        display_execution(res)


def run_interactive() -> None:
    orchestrator = ToolChainOrchestrator()
    print("\nEntering Interactive Mode. Type any question, request, or 'help'/'exit'.")
    while True:
        try:
            user_input = input("\nEnter your request > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting Day 20 Tool Engine. Goodbye!")
                break
            if user_input.lower() == "help":
                print("\nTry queries like:")
                print(" - Calculate (25 + 15) * 2")
                print(" - What's the weather in Kolkata?")
                print(" - What day is 25 September 2026?")
                print(" - Read employees.csv and calculate the average salary")
                print(" - Get the weather in Kolkata and convert the temperature to Fahrenheit")
                print(" - Find all Engineering employees from the database and calculate their average salary")
                print(" - Send an email to mentor@example.com with subject Update")
                continue

            result = orchestrator.execute_request(user_input)
            display_execution(result)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 20 Function Calling and Tool Chaining CLI")
    parser.add_argument("--demo", action="store_true", help="Run automated demonstration on sample queries")
    args = parser.parse_args()

    # Ensure DB initialized
    init_database()
    print_banner()

    if args.demo:
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
