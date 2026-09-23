# Day 20: Tool Creation, Function Calling & Tool Chaining Engine

An enterprise-ready, modular agentic tool execution framework built in Python 3.12 for autonomous software engineering workflows. Features 8 discrete production-grade tools, a dual-routing function calling layer (offline deterministic router + OpenAPI/JSON Schema generator for LLMs), multi-tool pipeline chaining, centralized exception containment, an interactive CLI, and comprehensive test coverage.

---

## 1. Today's Learning Objectives

- **Tool Creation**: Formalizing standalone functional capabilities into standardized, schema-driven, self-documenting modules.
- **Function Calling**: Implementing intent detection, parameter extraction, and dynamic dispatch from natural language without brittle hardcoded logic.
- **Tool Chaining**: Constructing sequential multi-tool pipelines where intermediate data passes between tools before producing a final synthesis.
- **Error Handling**: Engineering defensive guardrails, input validation, and centralized exception translation returning standardized diagnostic JSON payloads instead of crashing.

---

## 2. What is a Tool?

In modern AI agent architectures, a **Tool** is a specialized, executable software component that extends the capabilities of a language model or reasoning agent beyond its static parameters. While LLMs excel at language comprehension and reasoning, they cannot natively query databases, perform deterministic floating-point arithmetic, inspect local file systems, or interface with external APIs.

A well-architected Tool encapsulates:
1. **Identity & Metadata**: A unique identifier and clear descriptive intent.
2. **Schema Contract**: An explicit JSON Schema defining accepted arguments, required types, and constraints.
3. **Execution Logic**: Deterministic, idempotent, or safe execution logic.
4. **Validation & Sandboxing**: Input validation and defensive boundaries (e.g., path traversal prevention, SQL injection sanitization, safe AST expression evaluation).
5. **Standardized Response Envelope**: Uniform JSON format reporting `success`, `data`, or granular `error` diagnostics.

---

## 3. Architecture

```text
                                User Request
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │  Function Calling Router  │
                       │  - Deterministic Intent   │
                       │  - LLM Schema Generator   │
                       └─────────────┬─────────────┘
                                     │
                                     ▼
                        Workflow & Tool Selection
                                     │
        ┌───────────────┬────────────┴──┬──────────────┬──────────────┐
        ▼               ▼               ▼              ▼              ▼
   ┌─────────┐    ┌───────────┐   ┌───────────┐   ┌─────────┐   ┌───────────┐
   │Calculator│   │Web Search │   │ Database  │   │  File   │   │  Weather  │
   │  (AST)  │    │(Live/Mock)│   │ (SQLite)  │   │ Reader  │   │(Live/Mock)│
   └─────────┘    └───────────┘   └───────────┘   └─────────┘   └───────────┘
        │               │               │              │              │
        └───────┬───────┴───────────────┼──────────────┴──────────────┘
                │                       ▼
                │           ┌───────────────────────┐
                │           │   Tool Chaining Bus   │
                │           │ (Step N -> Step N+1)  │
                │           └───────────┬───────────┘
                │                       │
                │                       ▼
                │             ┌───────────────────┐
                │             │   Data Analyzer   │
                │             │  / Email Sandbox  │
                │             └─────────┬─────────┘
                │                       │
                ▼                       ▼
   ┌────────────────────────────────────────────────────────┐
   │            Standardized Output / Error Format           │
   └────────────────────────────┬───────────────────────────┘
                                │
                                ▼
                          Final Response
```

---

## 4. Tools Implemented

All tools inherit from the abstract base class `BaseTool` defined in `tools/base.py`:

```
BaseTool
 ├── name: str
 ├── description: str
 ├── parameters: Dict[str, Any] (JSON Schema)
 ├── examples: List[Dict[str, Any]]
 ├── validate_inputs(kwargs) -> None
 ├── run(**kwargs) -> Any
 ├── execute(**kwargs) -> Dict[str, Any]
 └── to_function_schema() -> Dict[str, Any]
```

### 1. Calculator (`tools/calculator.py`)
- **Purpose**: Evaluates arithmetic expressions, percentages, and averages.
- **Safety**: Uses Python's Abstract Syntax Tree (`ast.parse`) parser and explicit operator whitelist (`ast.Add`, `ast.Sub`, `ast.Mult`, `ast.Div`, `ast.Mod`, `ast.Pow`, etc.). Strictly **does not use** unsafe `eval()`.
- **Supported Syntaxes**:
  - Binary arithmetic: `25 * 48`, `100 / 4`, `(25 + 15) * 2`
  - Percentages: `15% of 800` &rarr; `120`
  - Averages: `Average of 10, 20, 30` &rarr; `20`
- **Output**: `{"expression": "...", "result": 1200, "status": "success"}`

### 2. Web Search (`tools/web_search.py`)
- **Purpose**: Retrieves online articles, documentation, and news snippets.
- **Dual-Mode**: Connects to live search APIs when `WEB_SEARCH_API_KEY` is configured; otherwise gracefully falls back to an offline simulated knowledge base clearly labelled `source: "mock (offline mode)"`.
- **Output**: `{"query": "...", "total_results": 4, "source": "...", "results": [{"title": "...", "url": "...", "snippet": "..."}]}`

### 3. Database Tool (`tools/database.py`)
- **Purpose**: Safe query interface for local SQLite relational database (`data/app.db`).
- **Data Model**:
  - `employees` (`id`, `name`, `department`, `role`, `salary`)
  - `projects` (`id`, `name`, `status`, `owner`)
- **Security & Guardrails**: Enforces parameterized SQL queries (`?` placeholders). Strictly forbids destructive SQL operations (`DROP`, `DELETE`, `ALTER`, `TRUNCATE`, `INSERT`, `UPDATE`).
- **Output**: `{"query": "...", "parameters": [...], "columns": [...], "row_count": 5, "rows": [...]}`

### 4. File Reader (`tools/file_reader.py`)
- **Purpose**: Reads and parses local repository files (`.txt`, `.md`, `.json`, `.csv`).
- **Security**: Directory sandboxing prevents path traversal attacks (`..` or escaping directory).
- **Format Intelligence**: Auto-parses JSON into Python dictionaries and CSV into parsed records with headers and row counts.
- **Output**: `{"filename": "...", "metadata": {"extension": ".csv", "size_bytes": 512}, "content": {...}}`

### 5. Weather Tool (`tools/weather.py`)
- **Purpose**: Provides meteorological conditions (temperature, condition, humidity, wind speed) for cities worldwide.
- **Dual-Mode**: Live OpenWeatherMap integration via `WEATHER_API_KEY`, with automatic fallback to high-fidelity mock weather data.
- **Output**: `{"location": "Kolkata", "temperature": 28.5, "condition": "Partly Cloudy", "humidity": "72%", "wind_speed": "12 km/h", "source": "..."}`

### 6. Email Tool (`tools/email_tool.py`)
- **Purpose**: Validates, drafts, and dispatches email communications.
- **Safety**: Operates in safe sandbox queue mode by default, preventing accidental live email dispatches. Validates RFC-compliant email syntax on recipients, CC, and BCC.
- **Output**: `{"status": "queued_sandbox", "mode": "sandbox", "envelope": {"to": "...", "subject": "...", "cc": []}, "body_preview": "..."}`

### 7. Date Tool (`tools/date_tool.py`)
- **Purpose**: Calendar arithmetic and temporal calculations using Python's `datetime` and `dateutil`.
- **Supported Operations**:
  - `current`: Current local date, time, weekday, and ISO timestamp.
  - `day_of_week`: Weekday lookup for historical or future dates (e.g., "25 September 2026" &rarr; "Friday").
  - `days_between`: Absolute and relative day difference between two dates.
  - `add_days`: Future or past date offset calculations.
  - `convert_format`: Custom strftime formatting conversions.

### 8. Data Analyzer (`tools/data_analyzer.py`)
- **Purpose**: Statistical profiling and aggregation for tabular datasets (CSV, JSON, or in-memory rows from previous tool steps).
- **Capabilities**:
  - Row and column tallies
  - Missing value counts per column
  - Descriptive statistics: `mean`, `median`, `min`, `max`, `count`
  - Group-by aggregation (e.g., average salary grouped by department)
  - Correlation matrices across numeric columns

---

## 5. Function Calling

### What is Function Calling?
Function calling allows an agent or language model to translate user intent into structured JSON payloads describing which tool to run and with what arguments, rather than attempting to guess or hallucinate text answers.

### Rule-Based Selection vs. LLM-Based Function Calling

| Feature | Rule-Based Tool Selection (Deterministic) | LLM-Based Function Calling |
|---|---|---|
| **Latency** | Sub-millisecond execution | Network latency dependent (1-3s) |
| **Cost** | Zero API cost, works 100% offline | Consumes token budget |
| **Reliability** | Deterministic, strict pattern/intent rules | Probabilistic, handles extreme conversational ambiguity |
| **Tool Extensibility** | Requires rule definition per tool | Generalizes across tool schemas automatically |
| **Deployment** | Runs anywhere with standard Python | Requires external API keys or local weights |

This repository implements **both**:
1. A **Deterministic Intent Router** (`core/router.py`) running locally without external credentials.
2. A **Tool Schema Exporter** (`get_tools_schema()`) generating OpenAI / Google Gemini function schemas for LLM-based autonomous agents.

---

## 6. Tool Chaining (5 Demonstrated Pipelines)

Tool chaining passes the output of an initial tool as input to a subsequent tool to accomplish compound requests.

```
User Request ──► Tool 1 ──► Tool 1 Output ──► Tool 2 ──► Final Synthesis
```

### Chain 1: File Reader &rarr; Data Analyzer
- **User Request**: *"Read employees.csv and calculate the average salary."*
- **Step 1 (`file_reader`)**: Reads `data/employees.csv` from disk, parses records.
- **Step 2 (`data_analyzer`)**: Ingests tabular rows and calculates mean of `salary`.
- **Final Result**: `"Successfully read 'employees.csv' (10 records). Statistical Analysis: Mean salary is $67,500.00 (Median: $66,500.00)."`

### Chain 2: Weather Tool &rarr; Calculator
- **User Request**: *"Get the weather in Kolkata and convert the temperature to Fahrenheit."*
- **Step 1 (`weather`)**: Fetches Kolkata reading (`temperature = 28.5` °C).
- **Step 2 (`calculator`)**: Evaluates `(28.5 * 9 / 5) + 32` via AST.
- **Final Result**: `"Current weather in Kolkata: 28.5°C (83.3°F). Condition: Partly Cloudy, Humidity: 72%."`

### Chain 3: Database Tool &rarr; Data Analyzer
- **User Request**: *"Find all Engineering employees from the database and calculate their average salary."*
- **Step 1 (`database`)**: Executes `SELECT * FROM employees WHERE department = 'Engineering' AND salary > 50000`.
- **Step 2 (`data_analyzer`)**: Analyzes in-memory rows from the database query.
- **Final Result**: `"Database query retrieved 5 matching Engineering records. Analyzed metrics: Average salary is $81,000.00 (Max: $95,000.00)."`

### Chain 4: File Reader &rarr; Data Analyzer
- **User Request**: *"Read the project status from sample.json and prepare a summary."*
- **Step 1 (`file_reader`)**: Reads `data/sample.json`.
- **Step 2 (`data_analyzer`)**: Profiles milestones and status metrics.
- **Final Result**: `"Project Summary for 'Project Antigravity Agent': Status is 'In Progress', Owner: Alice Johnson, Budget: $125,000.00, Completion: 67%."`

### Chain 5: Weather Tool &rarr; Email Tool
- **User Request**: *"Find current weather for Kolkata and email the result to mentor@example.com."*
- **Step 1 (`weather`)**: Retrieves weather for Kolkata.
- **Step 2 (`email`)**: Composes email body with temperature and conditions, queuing to sandbox.
- **Final Result**: `"Fetched current weather for Kolkata (28.5°C, Partly Cloudy) and queued automated email briefing to mentor@example.com."`

---

## 7. Error Handling Strategy

All tools enforce defensive validation and error containment via `core/errors.py`. Errors never cause unhandled tracebacks or crash the application; instead, they produce standardized JSON payloads:

```json
{
  "success": false,
  "error": {
    "type": "ValidationError",
    "message": "Division by zero is undefined.",
    "tool": "calculator"
  }
}
```

### Handled Error Scenarios
- **Invalid Calculator Expression**: `50 / 0` &rarr; `ValidationError: Division by zero is undefined.`
- **Code Execution Attack**: `__import__('os').system('dir')` &rarr; `ValidationError: Malformed mathematical expression.`
- **Empty Search Query**: `""` &rarr; `ValidationError: Search query cannot be empty.`
- **Database Destructive SQL**: `DROP TABLE employees` &rarr; `SecurityError: Only SELECT queries are allowed.`
- **Path Traversal Attack**: `../../Windows/System32` &rarr; `SecurityError: Path traversal access denied.`
- **Missing File**: `data/missing.txt` &rarr; `ResourceNotFoundError: File not found.`
- **Unsupported File Extension**: `script.py` &rarr; `ValidationError: Unsupported file format '.py'.`
- **Invalid Email Address**: `not-an-email` &rarr; `ValidationError: Invalid email address.`
- **Missing Email Subject/Body**: `subject=""` &rarr; `ValidationError: Email subject line cannot be empty.`
- **Invalid Calendar Date**: `"xyz"` &rarr; `ValidationError: Invalid date format.`
- **Empty Dataset**: `data=[]` &rarr; `ValidationError: Provided 'data' is empty.`

---

## 8. Function Calling Decision Matrix

The complete 14-request decision table is maintained in [`decision_matrix.md`](decision_matrix.md):

| # | User Request | Tool/Function | Tool Chaining? | Why This Tool? |
|---|---|---|---|---|
| **1** | *"Calculate 45 * 23"* | `calculator` | No | Pure arithmetic expression evaluated safely via AST parser. |
| **2** | *"What's the weather in Kolkata?"* | `weather` | No | Real-time meteorological inquiry for a specific city. |
| **3** | *"Search the web for the latest AI news."* | `web_search` | No | Open-ended external information retrieval across web indices. |
| **4** | *"Read internship_notes.md"* | `file_reader` | No | Local repository file access protected by sandboxing. |
| **5** | *"Find Engineering employees earning above 50000."* | `database` | No | Parameterized SQL query on relational SQLite tables. |
| **6** | *"What date will it be 45 days from today?"* | `date_tool` | No | Calendar arithmetic with month boundary and leap year support. |
| **7** | *"Analyze employees.csv."* | `data_analyzer` | No | Tabular statistical profiling (mean, median, nulls). |
| **8** | *"Send an email to my mentor with today's internship update."* | `email` | No | Outbound communication validated and queued in sandbox. |
| **9** | *"Read employees.csv and calculate the average salary."* | `file_reader` &rarr; `data_analyzer` | **Yes** | Reads file first, then pipes data to statistical aggregator. |
| **10** | *"Get the weather in Kolkata and convert the temperature to Fahrenheit."* | `weather` &rarr; `calculator` | **Yes** | Fetches Celsius reading, then calculates `(C * 9/5) + 32`. |
| **11** | *"Find all Engineering employees from the database and calculate their average salary."* | `database` &rarr; `data_analyzer` | **Yes** | Queries SQLite rows, then aggregates salary metrics. |
| **12** | *"Read the project status from sample.json and prepare a summary."* | `file_reader` &rarr; `data_analyzer` | **Yes** | Reads JSON schema, then computes milestone completion rate. |
| **13** | *"Find current weather for Kolkata and email the report."* | `weather` &rarr; `email` | **Yes** | Retrieves atmospheric data and composes automated email. |
| **14** | *"Days between 1947-08-15 and 1950-01-26"* | `date_tool` | No | Calendar diff between historical dates. |

---

## 9. Setup & How to Run

### Installation
Dependencies are lightweight and standard:
```bash
pip install -r requirements.txt
```

### Environment Variables (Optional)
The system operates seamlessly offline in safe mock/sandbox mode. To enable live external services, set:
```bash
# Web Search (optional)
export WEB_SEARCH_API_KEY="your-api-key"

# Live Weather (optional)
export WEATHER_API_KEY="your-openweathermap-key"

# Live Email (optional - default is safe sandbox)
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="user@example.com"
export SMTP_PASS="password"
```

### Running the Interactive CLI
Launch the interactive command line prompt:
```bash
python main.py
```

### Running the Automated Demo
Run all 12 representative demo queries with full traces:
```bash
python main.py --demo
```

### Running the Test Suite
Execute all 63 unit and integration tests:
```bash
python -m pytest tests/ -v
```

---

## 10. Verification Results

- **Total Test Cases**: 63
- **Passed**: 63 (100%)
- **Failed**: 0
- **Execution Time**: ~1.2s
- **Zero API Keys Required**: Complete local and offline autonomy with verified safety.
