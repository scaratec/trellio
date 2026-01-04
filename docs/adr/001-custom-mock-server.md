# ADR 001: Custom Mock Server and Validation Strategy

*   **Status:** Accepted
*   **Date:** 2026-01-03
*   **Context:**
    We are building `trellio`, an asynchronous Python client for the Trello API. We need a reliable way to test our library against the Trello API without relying on the actual (rate-limited, stateful) production API for every test run. Ideally, we would generate a mock server from an official OpenAPI specification using tools like Mockoon. However, Trello does not provide an official, complete OpenAPI spec.

*   **Decision:**
    1.  **Implement a Custom Mock Server:** We will implement a lightweight, thread-safe mock server in Python (using `http.server`) directly within the test environment (`features/environment.py`). This server will simulate the subset of the Trello API required for our current scope.
    2.  **Validate Mock with `py-trello`:** To ensure our mock server behaves correctly (i.e., like the real Trello API), we will validate it using `py-trello`, an established and widely used synchronous Trello library. If `py-trello` can successfully interact with our mock server, we consider the mock behavior "correct enough" to develop our own library against it.
    3.  **Use `behave` for BDD:** We use `behave` to drive the development of our library, testing strictly against this validated mock.

*   **Consequences:**
    *   **Positive:**
        *   Full control over the test environment and state.
        *   No external dependencies on third-party mock services or complex Docker setups for Mockoon.
        *   High confidence in correctness due to validation against a reference implementation.
        *   Fast test execution.
    *   **Negative:**
        *   We must manually maintain the mock server code. If Trello's API changes, we have to update our mock.
        *   The mock server implementation adds code complexity to the test suite.
