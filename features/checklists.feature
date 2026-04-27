Feature: Trello Checklists Management

  As a user of the trellio library
  I want to manage checklists and check items on cards
  So that I can break down tasks into sub-tasks

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Checklist Board"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "Checklist Card"

  Scenario Outline: Create a checklist on a card
    When I create a checklist with name "<checklist_name>" on the card
    Then the checklist should be created successfully
    And the checklist name should be "<checklist_name>"
    And the checklist should belong to the card
    And retrieving the checklist by ID should show name "<checklist_name>"

    Examples:
      | checklist_name   |
      | Acceptance Tests |
      | Deploy Steps     |

  Scenario: Get a checklist
    Given a checklist exists on the card with name "Review Checklist"
    When I retrieve the checklist by its ID
    Then the retrieved checklist name should be "Review Checklist"

  Scenario: List all checklists on a card
    Given a checklist exists on the card with name "QA Checklist"
    And a checklist exists on the card with name "Deploy Checklist"
    When I list all checklists on the card
    Then I should see exactly 2 checklists
    And one of the checklists should have name "QA Checklist"
    And one of the checklists should have name "Deploy Checklist"

  Scenario: Delete a checklist
    Given a checklist exists on the card with name "Temporary Checklist"
    When I delete the checklist
    Then retrieving the deleted checklist should fail with a 404 error

  Scenario Outline: Add a check item to a checklist
    Given a checklist exists on the card with name "Item Checklist"
    When I add a check item with name "<item_name>" to the checklist
    Then the check item should be created successfully
    And the check item name should be "<item_name>"
    And the check item state should be "incomplete"

    Examples:
      | item_name        |
      | Write unit tests |
      | Update docs      |

  Scenario Outline: Add a check item with a position
    Given a checklist exists on the card with name "Position Checklist"
    When I add a check item with name "<item_name>" and position "<pos>"
    Then the check item should be created successfully
    And the check item name should be "<item_name>"

    Examples:
      | item_name      | pos    |
      | Top item       | top    |
      | Bottom item    | bottom |

  Scenario Outline: Update check item state
    Given a checklist exists on the card with name "State Checklist"
    And a check item exists in the checklist with name "Toggle Item"
    When I update the check item state to "<new_state>"
    Then the check item state should now be "<new_state>"

    Examples:
      | new_state  |
      | complete   |
      | incomplete |

  Scenario Outline: Update check item name
    Given a checklist exists on the card with name "Rename Checklist"
    And a check item exists in the checklist with name "Original Name"
    When I update the check item name to "<new_name>"
    Then the check item name should now be "<new_name>"

    Examples:
      | new_name           |
      | Renamed item alpha |
      | Renamed item beta  |

  Scenario Outline: Update check item position
    Given a checklist exists on the card with name "Reorder Checklist"
    And a check item exists in the checklist with name "Movable Item"
    When I update the check item position to "<pos>"
    Then the check item should still have name "Movable Item"

    Examples:
      | pos    |
      | top    |
      | bottom |

  Scenario: Delete a check item
    Given a checklist exists on the card with name "Delete Item Checklist"
    And a check item exists in the checklist with name "Disposable Item"
    When I delete the check item
    Then retrieving the checklist should not include check item "Disposable Item"

  Scenario: Fail to create a checklist without a name
    When I attempt to create a checklist without a name on the card
    Then the request should fail with a 400 error

  Scenario: Fail to get a non-existent checklist
    When I retrieve a checklist with ID "nonexistent_checklist_123"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent checklist
    When I delete a checklist with ID "nonexistent_checklist_123"
    Then the request should fail with a 404 error
