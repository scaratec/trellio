Feature: Trello Authentication

  As a user of the trellio library
  I want to authenticate with my Trello API Key and Token
  So that I can access my Trello data securely

  Background:
    Given a Trellio client with base URL "http://127.0.0.1:3000"

  Scenario: Successful Authentication check
    Given I have a valid API Key "valid_api_key"
    And I have a valid API Token "valid_api_token"
    When I check my member information
    Then the response should indicate a successful connection
    And my username should be "edgar_bot"
    And my full name should be "Edgar Bot"

  Scenario: Failed Authentication with invalid key
    Given I have an invalid API Key "invalid_key"
    And I have a valid API Token "valid_api_token"
    When I check my member information
    Then the request should fail with a 401 error
    And the error message should contain "invalid key"
