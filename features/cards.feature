Feature: Trello Cards Management

  As a user of the trellio library
  I want to manage my Trello cards
  So that I can track tasks and progress

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Card Board"
    And a list exists on that board with name "To Do"

  Scenario: Create a new card
    When I create a new card with name "Implement Feature X" in the "To Do" list
    Then the card should be created successfully
    And the card name should be "Implement Feature X"
    And the card should belong to the "To Do" list

  Scenario: Get a specific card
    Given a card exists in "To Do" with name "Existing Card"
    When I retrieve the card by its ID
    Then the retrieved card name should be "Existing Card"

  Scenario: Update a card
    Given a card exists in "To Do" with name "Old Card Name"
    When I update the card name to "New Card Name"
    Then the card name should now be "New Card Name"

  Scenario: Update card description
    Given a card exists in "To Do" with name "Desc Card"
    When I update the card description to "This is a detailed description"
    Then the card description should be "This is a detailed description"

  Scenario: Delete a card
    Given a card exists in "To Do" with name "To Delete Card"
    When I delete the card
    Then the card should no longer exist
