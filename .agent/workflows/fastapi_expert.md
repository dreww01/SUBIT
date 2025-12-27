---
description: Expert guide for debugging, writing, and testing FastAPI applications.
---

# FastAPI Expert Workflow

Use this checklist and guide when working on FastAPI projects to ensure adherence to modern best practices and efficient debugging.

## 1. Preparation & Documentation
- **Pydantic Version**: Verify if the environment uses Pydantic V1 or V2. Default to **V2** best practices unless constrained.
- **Doc Search**: If unsure about specific feature syntax (e.g., specific auth flows), search [FastAPI Docs](https://fastapi.tiangolo.com/).

## 2. Writing Code: Modern Best Practices

### Type Hints & Dependency Injection
- **Use `Annotated`**: Standardize on `Annotated` for `Depends`, `Query`, `Path`, `Body`.
    - *Modern Pattern*: `commons: Annotated[CommonParams, Depends(CommonParams)]`
    - *Avoid*: Plain default values for `Depends` in the signature without `Annotated` if possible for clarity.
- **Pydantic V2 Usage**:
    - Use `model_config = ConfigDict(...)` instead of `class Config`.
    - Use `model_validate`, `model_dump`, `model_dump_json` instead of `parse_obj`, `dict`, `json`.
    - Use `Field(description="...")` to document schemas for the OpenAPI spec.

### Application Architecture
- **Lifespan Events**:
    - **MUST** use `@asynccontextmanager` for startup/shutdown logic.
    - **avoid** `@app.on_event("startup")` (deprecated).
    ```python
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Connect DB
        yield
        # Shutdown: Close DB
    app = FastAPI(lifespan=lifespan)
    ```
- **Routers**: Use `APIRouter` to split code into modules (`users.py`, `items.py`).
- **Dependencies Global vs Local**: Put security dependencies on the `APIRouter` or `FastAPI` instance if they apply to all routes.

## 3. Debugging Techniques

### Validation Errors (422)
- **Read the Response**: The 422 body contains a `detail` list. Each item has:
    - `loc`: Location of error (e.g., `["body", "user", "email"]`).
    - `msg`: Error message.
    - `type`: Error type.
- **Pydantic Debugging**: If data isn't validating, print `model.model_dump()` to see *exactly* what is being passed.

### Server Errors (500)
- **Log Tracebacks**: Ensure exceptions are not swallowed. Use `logging` or print tracebacks in dev.
- **Local Testing**: Run with `uvicorn main:app --reload` to catch errors instantly.

## 4. Testing Strategy

### Tools
- **Pytest**: The standard runner.
- **TestClient**: `from fastapi.testclient import TestClient`. Wraps `httpx` for synchronous testing of async endpoints (magic!).
- **Async Testing**: `AsyncClient` from `httpx` for true async integration tests (necessary for testing listeners or background tasks).

### Test Structure
- **Fixtures**: Create a `conftest.py` with:
    - `client` fixture.
    - `db` session fixture (rollback transaction after each test).
- **Happy Path & Edge Cases**: Test valid input *and* boundary conditions (missing fields, wrong types).

## 5. Implementation Checklist
- [ ] `Annotated` used for all DI?
- [ ] Startup/Shutdown logic in `lifespan`?
- [ ] Pydantic models use `ConfigDict` (if V2)?
- [ ] `APIRouter` used for modularity?
- [ ] `pytest` configured in `pyproject.toml` or via `conftest.py`?
