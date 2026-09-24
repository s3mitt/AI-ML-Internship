# API Documentation

## 1. Overview & Base Configuration

This documentation specifies the endpoints, schemas, validation rules, and response headers for the **FastAPI Async Performance Demo** application.

- **Base URL**: `http://127.0.0.1:8000`
- **Current API Version**: `v1` (`/api/v1`)
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 2. Global Headers & Middleware

Every HTTP response returned by the server automatically includes the diagnostic header injected by `TimingMiddleware`:

| Header Name | Type | Description | Example |
|---|---|---|---|
| `X-Process-Time` | string (float) | Total server processing time in seconds | `0.052134` |

---

## 3. Endpoints

### 3.1. Synchronous Item Processing

- **Route**: `POST /api/v1/items/sync`
- **Method**: `POST`
- **Summary**: Process Item Synchronously
- **Description**: Processes an item using synchronous blocking code (`def` + `time.sleep()`). FastAPI executes this route inside an external threadpool worker. Dispatches a post-response audit log via `BackgroundTasks`.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "Laptop",
  "quantity": 2,
  "price": 75000.0
}
```

#### Response Body (`200 OK`)
```json
{
  "id": "a64256f9-15b3-4745-8892-3bc70cbe57cf",
  "name": "Laptop",
  "quantity": 2,
  "price": 75000.0,
  "total_price": 150000.0,
  "status": "completed",
  "processing_type": "sync",
  "processed_at": "2026-09-24T12:25:50.436482+00:00",
  "message": "Item 'Laptop' processed successfully via synchronous pipeline."
}
```

#### cURL Example
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/sync" \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "quantity": 2, "price": 75000.0}'
```

---

### 3.2. Asynchronous Item Processing

- **Route**: `POST /api/v1/items/async`
- **Method**: `POST`
- **Summary**: Process Item Asynchronously
- **Description**: Processes an item using asynchronous non-blocking code (`async def` + `await asyncio.sleep()`). The single-threaded event loop yields control while waiting for simulated I/O. Dispatches a post-response audit log via `BackgroundTasks`.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "Laptop",
  "quantity": 2,
  "price": 75000.0
}
```

#### Response Body (`200 OK`)
```json
{
  "id": "98da79d3-5d0e-42fb-a4e4-e81a1a9e2201",
  "name": "Laptop",
  "quantity": 2,
  "price": 75000.0,
  "total_price": 150000.0,
  "status": "completed",
  "processing_type": "async",
  "processed_at": "2026-09-24T12:25:50.507604+00:00",
  "message": "Item 'Laptop' processed successfully via asynchronous pipeline."
}
```

#### cURL Example
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/async" \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "quantity": 2, "price": 75000.0}'
```

---

### 3.3. Health Check

- **Route**: `GET /api/v1/items/health`
- **Method**: `GET`
- **Summary**: V1 API Health Check
- **Response (`200 OK`)**:
```json
{
  "status": "ok",
  "version": "v1"
}
```

---

### 3.4. Root Welcome & Directory

- **Route**: `GET /`
- **Method**: `GET`
- **Summary**: Application Welcome & Meta
- **Response (`200 OK`)**:
```json
{
  "app_name": "FastAPI Async Performance Demo",
  "version": "1.0.0",
  "status": "online",
  "documentation": {
    "swagger_ui": "/docs",
    "redoc": "/redoc",
    "openapi_json": "/openapi.json"
  },
  "endpoints": {
    "sync_processing": "/api/v1/items/sync",
    "async_processing": "/api/v1/items/async",
    "health_check": "/api/v1/items/health"
  }
}
```

---

## 4. Request Validation & Error Specifications

All incoming payloads are strictly validated using Pydantic schema constraints.

### Schema Fields (`ItemCreate`)

| Field | Type | Constraint | Error on Violation |
|---|---|---|---|
| `name` | string | `min_length=2`, `max_length=100`, Required | `422 Unprocessable Entity` |
| `quantity` | integer | `gt=0` (strictly positive), Required | `422 Unprocessable Entity` |
| `price` | float | `gt=0.0` (strictly positive), Required | `422 Unprocessable Entity` |

### Sample Validation Errors (`422 Unprocessable Entity`)

#### Case A: Negative Quantity
**Payload**: `{"name": "Tablet", "quantity": -1, "price": 15000.0}`
**Response**:
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0",
      "input": -1,
      "ctx": { "gt": 0 }
    }
  ]
}
```

#### Case B: Negative Price
**Payload**: `{"name": "Tablet", "quantity": 1, "price": -500.0}`
**Response**:
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0",
      "input": -500.0,
      "ctx": { "gt": 0.0 }
    }
  ]
}
```

#### Case C: Missing Field
**Payload**: `{"quantity": 1, "price": 500.0}`
**Response**:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": { "quantity": 1, "price": 500.0 }
    }
  ]
}
```

---

## 5. Background Tasks Behavior

When an item is processed successfully (sync or async), the route registers a non-blocking background job:
- **Function**: `ItemService.log_background_audit`
- **Output Destination**: `logs/background_tasks.log`
- **Entry Structure**:
  ```text
  [2026-09-24T12:25:50.509209+00:00] AUDIT_EVENT | id=98da79d3-5d0e-42fb-a4e4-e81a1a9e2201 | name=Mechanical Mouse | type=async | client_ip=127.0.0.1 | status=AUDIT_RECORDED
  ```
- **Lifecycle Benefit**: The HTTP response is delivered to the user immediately, while non-critical file I/O finishes asynchronously in the background.
