Feature: Connection Lifecycle

  As a user of the trellio library
  I want the client to properly manage its HTTP connection
  So that I don't leak resources

  Background:
    Given a Trellio client with base URL "http://127.0.0.1:3000"

  Scenario: Client works as async context manager
    When I use the client as an async context manager with API Key "valid_api_key" and Token "valid_api_token"
    Then the response should indicate a successful connection
    And my username should be "edgar_bot"

  Scenario: Client can be explicitly closed
    When I create a client with API Key "valid_api_key" and Token "valid_api_token" and close it
    Then the client should be closed
