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
