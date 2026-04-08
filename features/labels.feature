Feature: Trello Labels Management

  As a user of the trellio library
  I want to manage labels on my Trello boards
  So that I can categorize and visually tag cards

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Labels Board"

  Scenario Outline: Create a label on a board
    When I create a label with name "<label_name>" and color "<color>" on the board
    Then the label should be created successfully
    And the label name should be "<label_name>"
    And the label color should be "<color>"
    And the label should belong to the board
    And listing labels on the board should include "<label_name>"

    Examples:
      | label_name | color |
      | Urgent     | red   |
      | Low Prio   | green |

  Scenario: List labels on a board
    Given a label exists on the board with name "Bug" and color "red"
    And a label exists on the board with name "Enhancement" and color "blue"
    When I list labels on the board
    Then I should see exactly 2 labels
    And one of the labels should have name "Bug"
    And one of the labels should have name "Enhancement"

  Scenario Outline: Update a label
    Given a label exists on the board with name "<old_name>" and color "<old_color>"
    When I update the label name to "<new_name>"
    Then the label name should now be "<new_name>"
    And listing labels on the board should include "<new_name>"

    Examples:
      | old_name | old_color | new_name  |
      | Draft    | yellow    | Published |
      | WIP      | orange    | Done      |

  Scenario: Delete a label
    Given a label exists on the board with name "Temporary" and color "sky"
    When I delete the label
    Then listing labels on the board should not include "Temporary"

  Scenario: Fail to create a label without a name
    When I attempt to create a label without a name on the board
    Then the request should fail with a 400 error

  Scenario: Fail to update a non-existent label
    When I update a label with ID "nonexistent_label_123" to name "Ghost"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent label
    When I delete a label with ID "nonexistent_label_123"
    Then the request should fail with a 404 error
