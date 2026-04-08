# Trellio - Async Trello API Client for Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Trellio** is a modern, asynchronous Python wrapper for the Trello API, built on top of `httpx`. It is designed to be lightweight, efficient, and easy to use in modern `asyncio` applications.

## Philosophy: BDD & Single Source of Truth

This project follows a strict **Behavior-Driven Development (BDD)** approach where the Gherkin feature files are the absolute **Single Source of Truth** for business logic (see [BDD Guidelines v1.8.0](https://github.com/your-org/bdd-guidelines)).

### What does this mean?

*   **Specification First:** All functionality is defined in `.feature` files (using Gherkin syntax) *before* any code is written.
*   **Living Documentation:** The feature files serve as both the requirement specification and the documentation of the library's behavior.
*   **Disposability & Regenerability:** Implementation code and step definitions are derivative artifacts. They could be re-implemented solely from the feature files.
*   **Validation:** The `behave` test suite ensures the implementation strictly adheres to the specified behavior.
*   **Data Explicitness:** All business-relevant data is visible in the feature files. No hidden constants in step code or mocks.
*   **Persistence Validation:** Write operations are independently verified through a second channel (re-GET after POST/PUT/DELETE).
*   **Anti-Hardcoding:** Critical fields use `Scenario Outline` with multiple data variants to prevent trivial hardcoding.

## Project Structure

```text
trellio/
├── features/                        # BDD Tests (Single Source of Truth)
│   ├── steps/
│   │   ├── common_steps.py          # Shared steps: client setup, error assertions
│   │   ├── auth_steps.py            # Authentication step definitions
│   │   ├── board_steps.py           # Board CRUD step definitions
│   │   ├── card_steps.py            # Card CRUD step definitions
│   │   └── list_steps.py            # List management step definitions
│   ├── authentication.feature       # Auth specs (happy + error paths)
│   ├── boards.feature               # Board CRUD specs (happy + error + server errors)
│   ├── cards.feature                # Card CRUD specs (happy + error + server errors)
│   ├── lists.feature                # List management specs (happy + error + server errors)
│   └── environment.py               # Test environment setup (mock server lifecycle)
│
├── src/
│   └── trellio/                     # Library source code
│       ├── __init__.py              # Public API exports
│       ├── client.py                # Async TrellioClient (httpx)
│       └── models.py                # Pydantic models (Member, Board, List, Card)
│
├── tests/
│   ├── mock_server.py               # Custom Trello API mock server
│   └── validation/
│       └── test_mock_with_pytrello.py  # Mock validation against py-trello
│
├── docs/
│   └── adr/
│       ├── 001-custom-mock-server.md       # ADR: Custom mock server approach
│       ├── 002-mock-server-selection.md    # ADR: Mock strategy comparison
│       └── 003-failure-path-enumeration.md # ADR: Systematic failure path coverage
│
├── requirements.txt                 # Production dependencies (httpx, pydantic)
└── requirements-dev.txt             # Dev dependencies (behave, py-trello, pytest)
```

## Test Coverage

The BDD suite covers **4 features, 39 scenarios, 253 steps**:

| Feature        | Happy Paths | Error Paths | Server Errors | Total |
|----------------|-------------|-------------|---------------|-------|
| Authentication | 2 (Outline) | 4           | -             | 6     |
| Boards         | 5 (2 Outline) | 4         | 2 (429, 500)  | 11    |
| Cards          | 5 (3 Outline) | 5         | 2 (429, 500)  | 12    |
| Lists          | 2 (Outline) | 2           | 1 (429)       | 5     |
| **Total**      | **14**      | **15**      | **5**         | **39**|

All 27 identified failure paths are covered (see [ADR 003](docs/adr/003-failure-path-enumeration.md) for the full layer-by-layer enumeration).

## Testing & Mocking Strategy

Since Trello does not provide an official OpenAPI specification, we ensure correctness through a multi-stage process:

1.  **Mock Server (`tests/mock_server.py`):** A custom Python mock server simulates the Trello API with in-memory state, JSON error responses (400/401/404/429/500), and a `forced_error` mechanism for server error simulation.
2.  **Mock Validation (`tests/validation/`):** The established `py-trello` library validates that our mock behaves like the real Trello API.
3.  **BDD Specification (`features/`):** The `trellio` library is developed and tested against the validated mock using `behave`.

## Features

*   **Fully Asynchronous:** Built with `httpx` for non-blocking I/O.
*   **Authentication:** Trello API Key and Token mechanism.
*   **Core CRUD Operations:**
    *   **Boards:** List, create, read, update, delete.
    *   **Lists:** Create lists on boards.
    *   **Cards:** Full card lifecycle management (create, read, update, delete).
*   **Type Hinted:** Comprehensive type hints throughout.
*   **Domain Objects:** Pythonic models (`TrelloBoard`, `TrelloList`, `TrelloCard`) powered by **Pydantic**.

## Development Setup

### Prerequisites

*   Python 3.9+

### Installation

```bash
git clone https://github.com/yourusername/trellio.git
cd trellio

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# BDD test suite
PYTHONPATH=src python -m behave

# Mock validation tests
PYTHONPATH=src pytest tests/validation/
```

## Architecture Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [001](docs/adr/001-custom-mock-server.md) | Custom Mock Server and Validation Strategy | Accepted |
| [002](docs/adr/002-mock-server-selection.md) | Mock Strategy: Custom Python vs. MockServer | Accepted |
| [003](docs/adr/003-failure-path-enumeration.md) | Failure Path Enumeration | Accepted |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
