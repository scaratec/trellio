Feature: Trello Boards Management

  As a user of the trellio library
  I want to manage my Trello boards
  So that I can organize my projects

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario Outline: Create a new board
    When I create a new board with name "<board_name>"
    Then the board should be created successfully
    And the board name should be "<board_name>"
    And the board should have a valid ID
    And retrieving the board by ID should show name "<board_name>"

    Examples:
      | board_name        |
      | Project Edgar     |
      | Sprint Backlog 42 |

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

  Scenario Outline: Update a board
    Given a board exists with name "<old_name>"
    And I have the ID of that board
    When I update the board name to "<new_name>"
    Then the board name should now be "<new_name>"
    And retrieving the updated board by ID should show name "<new_name>"

    Examples:
      | old_name      | new_name      |
      | Old Name      | New Name      |
      | Alpha Release | Beta Release  |

  Scenario: Delete a board
    Given a board exists with name "To Delete"
    And I have the ID of that board
    When I delete the board
    Then the board should no longer exist

  Scenario: Fail to create a board without a name
    When I attempt to create a board without a name
    Then the request should fail with a 400 error

  Scenario: Fail to get a non-existent board
    When I retrieve a board with ID "nonexistent_id_123"
    Then the request should fail with a 404 error

  Scenario: Fail to update a non-existent board
    When I update a board with ID "nonexistent_id_123" to name "Ghost"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent board
    When I delete a board with ID "nonexistent_id_123"
    Then the request should fail with a 404 error

  Scenario: Server returns 429 rate limit error on board creation
    Given the server will respond with a 429 error "Rate limit exceeded"
    When I attempt to create a board with name "Rate Limited Board"
    Then the request should fail with a 429 error
    And the error message should contain "Rate limit exceeded"

  Scenario: Server returns 500 internal error on board retrieval
    Given a board exists with name "Server Error Board"
    And I have the ID of that board
    And the server will respond with a 500 error "Internal server error"
    When I retrieve the board by its ID expecting an error
    Then the request should fail with a 500 error
    And the error message should contain "Internal server error"
