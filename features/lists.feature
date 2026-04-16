Feature: Trello Lists Management

  As a user of the trellio library
  I want to manage my Trello lists
  So that I can organize work within boards

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "List Board"

  Scenario Outline: Create a new list on a board
    When I create a new list with name "<list_name>" on the board
    Then the list should be created successfully
    And the list name should be "<list_name>"
    And the list should belong to the board

    Examples:
      | list_name   |
      | To Do       |
      | In Progress |

  Scenario: List all lists on a board
    Given a list was created on the board with name "Backlog"
    And a list was created on the board with name "Done"
    When I list all lists on the board
    Then I should see exactly 2 lists
    And one of the lists should have name "Backlog"
    And one of the lists should have name "Done"

  # --- update_list ---
  # Anti-hardcoding (§2.3): Two variants prove update generalises.
  # Persistence validation (§4.3): Verify via get_list.

  Scenario Outline: Update a list name
    Given a list was created on the board with name "<old_name>"
    When I update the list name to "<new_name>"
    Then the updated list name should be "<new_name>"
    And retrieving the list by ID should show name "<new_name>"

    Examples:
      | old_name    | new_name     |
      | To Do       | Renamed List |
      | In Progress | Done Done    |

  Scenario: Archive a list
    Given a list was created on the board with name "Temporary"
    When I archive the list
    Then the list should be archived

  # --- Error paths ---

  Scenario: Fail to update a non-existent list
    When I attempt to update list with ID "nonexistent_list_123" to name "Ghost"
    Then the request should fail with a 404 error

  Scenario: Fail to create a list without a name
    When I attempt to create a list without a name on the board
    Then the request should fail with a 400 error

  Scenario: Fail to create a list without a board ID
    When I attempt to create a list with name "Orphan List" without a board ID
    Then the request should fail with a 400 error

  Scenario: Server returns 429 rate limit error on list creation
    Given the server will respond with a 429 error "Rate limit exceeded"
    When I attempt to create a list with name "Rate Limited List" on the board
    Then the request should fail with a 429 error
    And the error message should contain "Rate limit exceeded"
