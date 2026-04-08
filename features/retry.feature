Feature: Retry with Exponential Backoff

  As a user of the trellio library
  I want failed requests to be retried automatically on transient errors
  So that intermittent server issues don't break my workflow

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And retry is configured with max retries 3 and initial delay 0.0

  Scenario: Successful retry after transient 429 errors
    Given a board exists with name "Retry Board"
    And I have the ID of that board
    And the server will respond with a 429 error "Rate limit exceeded" for 2 requests
    When I retrieve the board by its ID
    Then the retrieved board name should be "Retry Board"

  Scenario: Successful retry after transient 500 error
    Given a board exists with name "Server Error Retry Board"
    And I have the ID of that board
    And the server will respond with a 500 error "Internal server error" for 1 requests
    When I retrieve the board by its ID
    Then the retrieved board name should be "Server Error Retry Board"

  Scenario Outline: Retry exhaustion raises error
    Given the server will respond with a <status> error "<message>" permanently
    When I attempt to list boards with retry
    Then the request should fail with a <status> error
    And the error message should contain "<message>"

    Examples:
      | status | message             |
      | 429    | Rate limit exceeded |
      | 503    | Service unavailable |

  Scenario: No retry on 4xx client errors
    When I retrieve a board with ID "nonexistent_id_123"
    Then the request should fail with a 404 error

  Scenario: Successful board creation after transient 429
    And the server will respond with a 429 error "Rate limit exceeded" for 1 requests
    When I create a new board with name "Created After Retry"
    Then the board should be created successfully
    And the board name should be "Created After Retry"
    And retrieving the board by ID should show name "Created After Retry"
