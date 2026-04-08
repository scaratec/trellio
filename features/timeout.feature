Feature: Request Timeout

  As a user of the trellio library
  I want requests to fail with an error after a configurable timeout
  So that a hanging server does not block my application indefinitely

  Background:
    Given a Trellio client with base URL "http://127.0.0.1:3000"

  Scenario: Request times out when server is too slow
    Given a Trellio client with timeout 0.1 seconds
    And the server will delay responses by 0.5 seconds
    When I attempt to get my member information with timeout
    Then the request should fail with a timeout error
    And the error message should contain "timed out"

  Scenario: Request succeeds within timeout
    Given a Trellio client with timeout 5.0 seconds
    When I get my member information
    Then the response should indicate a successful connection
