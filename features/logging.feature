Feature: Request Logging

  As an operator of a service using the trellio library
  I want all API requests and retries to be logged
  So that I can monitor and debug Trello API interactions

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And retry is configured with max retries 3 and initial delay 0.0
    And I am capturing log output from "trellio"

  Scenario: Successful requests are logged at debug level
    When I list all my boards
    Then the log should contain a DEBUG message matching "GET /1/members/me/boards 200"

  Scenario: Retries are logged at warning level
    Given a board exists with name "Log Retry Board"
    And I have the ID of that board
    And the server will respond with a 429 error "Rate limit exceeded" for 1 requests
    When I retrieve the board by its ID
    Then the log should contain a WARNING message matching "Retry 1"
    And the log should contain a DEBUG message matching "200"

  Scenario: Failed requests are logged at error level
    Given the server will respond with a 429 error "Rate limit exceeded" permanently
    When I attempt to list boards with retry
    Then the log should contain an ERROR message matching "429"
