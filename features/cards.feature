Feature: Trello Cards Management

  As a user of the trellio library
  I want to manage my Trello cards
  So that I can track tasks and progress

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Card Board"
    And a list exists on that board with name "To Do"

  Scenario Outline: Create a new card
    When I create a new card with name "<card_name>" in the "To Do" list
    Then the card should be created successfully
    And the card name should be "<card_name>"
    And the card should belong to the "To Do" list
    And retrieving the card by ID should show name "<card_name>"

    Examples:
      | card_name           |
      | Implement Feature X |
      | Fix Login Bug #7    |

  Scenario: Get a specific card
    Given a card exists in "To Do" with name "Existing Card"
    When I retrieve the card by its ID
    Then the retrieved card name should be "Existing Card"

  Scenario Outline: Update a card
    Given a card exists in "To Do" with name "<old_name>"
    When I update the card name to "<new_name>"
    Then the card name should now be "<new_name>"
    And retrieving the updated card by ID should show name "<new_name>"

    Examples:
      | old_name      | new_name      |
      | Old Card Name | New Card Name |
      | Draft Review  | Final Review  |

  Scenario Outline: Update card description
    Given a card exists in "To Do" with name "<card_name>"
    When I update the card description to "<description>"
    Then the card description should be "<description>"
    And retrieving the updated card by ID should show description "<description>"

    Examples:
      | card_name  | description                       |
      | Desc Card  | This is a detailed description    |
      | Notes Card | Acceptance criteria: see checklist |

  Scenario: Delete a card
    Given a card exists in "To Do" with name "To Delete Card"
    When I delete the card
    Then the card should no longer exist

  Scenario: Fail to create a card without a name
    When I attempt to create a card without a name in the "To Do" list
    Then the request should fail with a 400 error

  Scenario: Fail to create a card in a non-existent list
    When I create a card with name "Orphan" in list ID "nonexistent_list_123"
    Then the request should fail with a 400 error

  Scenario: Fail to get a non-existent card
    When I retrieve a card with ID "nonexistent_card_123"
    Then the request should fail with a 404 error

  Scenario: Fail to update a non-existent card
    When I update a card with ID "nonexistent_card_123" to name "Ghost"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent card
    When I delete a card with ID "nonexistent_card_123"
    Then the request should fail with a 404 error

  Scenario: Server returns 429 rate limit error on card creation
    Given the server will respond with a 429 error "Rate limit exceeded"
    When I create a card with name "Rate Limited Card" in list ID "any_list_id"
    Then the request should fail with a 429 error
    And the error message should contain "Rate limit exceeded"

  Scenario: Server returns 500 internal error on card retrieval
    Given the server will respond with a 500 error "Internal server error"
    When I retrieve a card with ID "any_id"
    Then the request should fail with a 500 error
    And the error message should contain "Internal server error"
