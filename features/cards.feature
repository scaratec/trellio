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

  Scenario: List all cards in a list
    Given a card exists in "To Do" with name "Card Alpha"
    And a card exists in "To Do" with name "Card Beta"
    When I list all cards in the "To Do" list
    Then I should see exactly 2 cards in the list
    And one of the cards should have name "Card Alpha"
    And one of the cards should have name "Card Beta"

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

  # --- add_label_to_card / remove_label_from_card ---
  # Persistence validation via independent channel (§4.3)
  # Verify labels are actually present on the card via get_card.

  Scenario Outline: Add a label to a card and verify via get_card
    Given a card exists in "To Do" with name "<card_name>"
    And a label exists on the board with name "<label_name>" and color "<color>"
    When I add the label to the card
    Then retrieving the card should show the label is attached

    Examples:
      | card_name    | label_name | color |
      | Label Task A | Urgent     | red   |
      | Label Task B | Feature    | green |

  # Anti-hardcoding (§2.3): two different labels prove accumulation

  Scenario: Add two labels to the same card and verify both persist
    Given a card exists in "To Do" with name "Multi-Label Card"
    And a label exists on the board with name "Bug" and color "red"
    And another label exists on the board with name "P1" and color "orange"
    When I add both labels to the card
    Then retrieving the card should show 2 labels attached

  Scenario Outline: Remove a label from a card and verify via get_card
    Given a card exists in "To Do" with name "<card_name>"
    And a label exists on the board with name "<label_name>" and color "<color>"
    And the label is attached to the card
    When I remove the label from the card
    Then retrieving the card should show 0 labels attached

    Examples:
      | card_name      | label_name | color  |
      | Unlabel Task A | Stale      | yellow |
      | Unlabel Task B | Done       | blue   |

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
