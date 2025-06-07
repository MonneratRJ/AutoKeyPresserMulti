# Contributing Guidelines

## Core Principles

- **Layered architecture:**
  - Model (Domain) → Controller (Application) → Database (Infrastructure) → Views (Presentation)
- **Model:** Pure business logic (no frameworks)
- **Database:** DB/API implementations
- **Dependency Rule:**
  - Views → Controller → Model ← Database

## Scalability Rules

- **Small apps:** Use functions + dataclasses. Use singleton-like patterns for shared state if needed.
- **Medium apps:** Split by feature (e.g., `employees/`, `accounting/`). Use interfaces (ABCs).
- **Large apps:** 1 class per file. Use Dependency Injection (DI).

## File Structure

- `model/`: Business entities and rules (pure logic)
- `controller/`: Use cases and orchestration (like MVC controllers)
- `database/`: DB/API implementations (SQL, external services)
- `views/`: API endpoints or GUI (FastAPI routes, PyQt screens)

## Error Handling

- Use custom exceptions (e.g., `EmployeeNotFoundError`)
- Wrap all external calls (no naked exceptions)

## Dynamic Scaling

- Start simple (flat structure)
- Split files when >300-500 lines
- Tag with `# SCALING: Split into model/employee.py if growing.`

## Key Keywords

- "Model first, frameworks last."
- "Depend on abstractions (ABC)."
- "1 class/file if complex."
- "Wrap errors, no naked exceptions."

## Example Flow

- Start with `main.py`
- Add DB? → Create `database/repositories/`
- Big feature? → Split into `model/feature/` + controller use cases

**Keep it simple. Scale only when needed.**
