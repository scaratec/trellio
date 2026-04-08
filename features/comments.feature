Feature: Trello Comments Management

  As a user of the trellio library
  I want to manage comments on Trello cards
  So that I can discuss tasks with my team

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Comments Board"
    And a list exists on that board with name "Discussion"
    And a card exists in "Discussion" with name "Comment Card"

  Scenario Outline: Add a comment to a card
    When I add a comment "<text>" to the card
    Then the comment should be created successfully
    And the comment text should be "<text>"
    And listing comments on the card should include "<text>"

    Examples:
      | text                             |
      | This looks good, ship it!        |
      | Needs revision on error handling |

  Scenario: List comments on a card
    Given a comment exists on the card with text "First comment"
    And a comment exists on the card with text "Second comment"
    When I list comments on the card
    Then I should see exactly 2 comments
    And one of the comments should have text "First comment"
    And one of the comments should have text "Second comment"

  Scenario Outline: Update a comment
    Given a comment exists on the card with text "<old_text>"
    When I update the comment text to "<new_text>"
    Then the comment text should now be "<new_text>"

    Examples:
      | old_text     | new_text          |
      | Draft note   | Final note        |
      | TODO: review | Reviewed and done |

  Scenario: Delete a comment
    Given a comment exists on the card with text "Temporary note"
    When I delete the comment
    Then listing comments on the card should not include "Temporary note"

  Scenario: Fail to add an empty comment
    When I attempt to add an empty comment to the card
    Then the request should fail with a 400 error

  Scenario: Fail to update a non-existent comment
    When I update a comment with ID "nonexistent_comment_123" to text "Ghost"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent comment
    When I delete a comment with ID "nonexistent_comment_123"
    Then the request should fail with a 404 error
