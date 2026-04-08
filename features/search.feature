Feature: Trello Search

  As a user of the trellio library
  I want to search for boards and cards by keyword
  So that I can quickly find resources in my Trello workspace

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario: Search boards by name
    Given a board exists with name "Project Alpha"
    And a board exists with name "Project Beta"
    And a board exists with name "Unrelated Board"
    When I search for "Project"
    Then the search results should contain 2 boards
    And one of the found boards should have name "Project Alpha"
    And one of the found boards should have name "Project Beta"

  Scenario: Search cards by name
    Given a board exists with name "Search Card Board"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "Fix login bug"
    And a card exists in "Tasks" with name "Fix signup bug"
    And a card exists in "Tasks" with name "Add dashboard"
    When I search for "bug"
    Then the search results should contain 2 cards
    And one of the found cards should have name "Fix login bug"
    And one of the found cards should have name "Fix signup bug"

  Scenario: Search with no results
    Given a board exists with name "Empty Search Board"
    When I search for "nonexistent_xyz_query"
    Then the search results should contain 0 boards
    And the search results should contain 0 cards

  Scenario: Search with limit
    Given a board exists with name "Limited A"
    And a board exists with name "Limited B"
    And a board exists with name "Limited C"
    When I search for "Limited" with limit 2
    Then the search results should contain at most 2 boards
