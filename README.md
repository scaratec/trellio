# Trellio - Async Trello API Client for Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Trellio** is a modern, asynchronous Python wrapper for the Trello API, built on top of `httpx`. It is designed to be lightweight, efficient, and easy to use in modern `asyncio` applications.

## 🚀 Philosophy: BDD & Single Source of Truth

This project follows a strict **Behavior-Driven Development (BDD)** approach where the Gherkin feature files are the absolute **Single Source of Truth**.

### What does this mean?

*   **Specification First:** All functionality is defined in `.feature` files (using Gherkin syntax) *before* any code is written.
*   **Living Documentation:** The feature files serve as both the requirement specification and the documentation of the library's behavior.
*   **Disposability & Regenerability:** The project structure and code are designed such that **implementation code (source) and test steps are considered derivative artifacts**. Theoretically, if you were to delete all Python source code and step definitions, they could be re-implemented solely based on the detailed specifications provided in the feature files.
*   **Validation:** The `behave` test suite ensures that the implementation strictly adheres to the behavior defined in the feature files.

## 📂 Project Structure

A concise overview of the project's layout and the purpose of key files:

```text
trellio/
├── features/                  # BDD Tests (Single Source of Truth)
│   ├── steps/
│   │   └── trellio_steps.py   # Step definitions implementing the .feature files
│   ├── authentication.feature # Gherkin specs for Auth
│   ├── boards.feature         # Gherkin specs for Board management
│   └── environment.py         # Test environment setup & Mock Server implementation
│
├── src/
│   └── trellio/               # The actual library source code
│       ├── __init__.py        # Exports public API
│       ├── client.py          # Main TrellioClient implementation (httpx)
│       └── models.py          # Pydantic data models (TrelloMember, TrelloBoard)
│
├── tests/
│   └── validation/            # Verification tests for the Mock Server
│       └── test_mock_with_pytrello.py # Validates our Mock against the reference lib
│
├── requirements.txt           # Production dependencies (httpx, pydantic)
└── requirements-dev.txt       # Dev dependencies (behave, py-trello, pytest)
```

## 🧪 Testing & Mocking Strategy

Since there is no official OpenAPI specification available, we ensure correctness through a multi-stage process:

1.  **Mock Server (`features/environment.py`):** We implement a custom Python-based mock server that simulates the Trello API. This server runs in a separate thread during tests.
2.  **Mock Validation (`tests/validation/`):** We use the established `py-trello` library as a reference client to test our mock server. If `py-trello` works against our mock, the mock is considered valid and compliant with Trello's actual behavior.
3.  **Library Implementation (`src/trellio/`):** Our new async library, `trellio`, is then implemented and tested against this validated mock server using the BDD features.

## 📦 Features (Initial Scope)

*   **Fully Asynchronous:** Built with `httpx` for non-blocking I/O.
*   **Authentication:** Supports the standard Trello **API Key and Token** mechanism.
*   **Core CRUD Operations:**
    *   **Boards:** List, create, read, update, delete.
    *   **Lists:** Manage lists within boards.
    *   **Cards:** Full card lifecycle management.
*   **Type Hinted:** Comprehensive type hints for better developer experience.
*   **Domain Objects:** Pythonic objects (`Board`, `List`, `Card`) powered by **Pydantic**.

## 🛠️ Development Setup

### Prerequisites

*   Python 3.9+
*   `uv` (recommended) or `pip`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/trellio.git
    cd trellio
    ```

2.  **Set up the environment:**
    ```bash
    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

### Running Tests

To execute the BDD test suite:

```bash
behave
```

This will parse the feature files in the `features/` directory and run the corresponding steps.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
