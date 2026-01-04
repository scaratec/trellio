Feature: Trello Boards Management

  As a user of the trellio library
  I want to manage my Trello boards
  So that I can organize my projects

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario: Create a new board
    When I create a new board with name "Project Edgar"
    Then the board should be created successfully
    And the board name should be "Project Edgar"
    And the board should have a valid ID

  Scenario: List all boards
    Given a board exists with name "Existing Board"
    When I list all my boards
    Then I should see at least 1 board
    And one of the boards should have name "Existing Board"

  Scenario: Get a specific board
    Given a board exists with name "Details Board"
    And I have the ID of that board
    When I retrieve the board by its ID
    Then the retrieved board name should be "Details Board"

  Scenario: Update a board
    Given a board exists with name "Old Name"
    And I have the ID of that board
    When I update the board name to "New Name"
    Then the board name should now be "New Name"

  Scenario: Delete a board
    Given a board exists with name "To Delete"
    And I have the ID of that board
    When I delete the board
    Then the board should no longer exist
