# ADR 002: Selection of Mocking Strategy (Custom Python Mock vs. MockServer)

*   **Status:** Accepted
*   **Date:** 2026-01-03
*   **Context:**
    To achieve "Feature Complete" status for `trellio`, we need a robust way to simulate the Trello API, including stateful CRUD operations (Boards, Lists, Cards). We evaluated two options:
    1.  **Custom Python Mock Server:** Extending our existing `http.server` implementation.
    2.  **MockServer (mock-server.com):** A Java/Docker-based solution for mocking HTTP/HTTPS.

*   **Decision:**
    We decide to **maintain and extend the Custom Python Mock Server**.

*   **Rationale:**
    *   **Statefulness:** Trello is a CRUD application. State management (creating an entity and reading it back) is trivial to implement in Python using in-memory dictionaries. Achieving the same stateful behavior in MockServer requires complex dynamic expectation logic or callbacks, which introduces unnecessary accidental complexity.
    *   **Developer Experience & Dependencies:** The custom mock requires only standard Python libraries. It runs anywhere Python runs, with zero overhead. MockServer introduces heavy dependencies (Java/Docker) that would complicate the setup for contributors and CI pipelines.
    *   **Control:** We have granular control over the mock's logic, allowing us to precisely simulate Trello's idiosyncrasies (e.g., specific error codes, trailing slashes) which we validate against the reference implementation `py-trello`.

*   **Consequences:**
    *   **Code Maintenance:** We accept the responsibility of writing and maintaining the mock logic in Python.
    *   **Refactoring:** As the mock logic grows with new features (Cards, Lists), we must ensure the codebase remains clean. We will refactor the mock server into its own module (`tests/mock_server.py`) to keep the test environment (`environment.py`) clean.
