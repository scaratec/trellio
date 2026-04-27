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

  Scenario Outline: Search cards scoped to a single board
    Given a board exists with name "<board_a_name>"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "<card_a_name>"
    And a board exists with name "<board_b_name>"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "<card_b_name>"
    When I search scoped to board "<board_a_name>" for "<query>"
    Then the search results should contain 1 card
    And the only found card should have name "<card_a_name>"

    Examples:
      | board_a_name  | card_a_name        | board_b_name  | card_b_name        | query    |
      | Alpha Project | Alpha sprint task  | Beta Project  | Beta sprint task   | sprint   |
      | Gamma Workspc | Gamma deploy ready | Delta Workspc | Delta deploy ready | deploy   |

  Scenario Outline: Search returns extended card fields
    Given a board exists with name "<board_name>"
    And a list exists on that board with name "<list_name>"
    And a card with description "<desc>" exists in "<list_name>" named "<card_name>"
    When I search for "<query>"
    Then the only found card should have name "<card_name>"
    And the only found card should have description "<desc>"
    And the only found card should belong to a list named "<list_name>"

    Examples:
      | board_name | list_name  | card_name        | desc                 | query   |
      | Sprint Bd  | Backlog    | Sprint planning  | Plan Q3 capacity     | Sprint  |
      | Release Bd | Up Next    | Release v2.1     | Cut tag and ship     | Release |
