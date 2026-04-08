Feature: Trello Members

  As a user of the trellio library
  I want to view board members and member details
  So that I can see who is working on what

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario: List members of a board
    Given a board exists with name "Team Board"
    And the board has a member with username "alice" and full name "Alice Smith"
    And the board has a member with username "bob" and full name "Bob Jones"
    When I list members of the board
    Then I should see exactly 2 members
    And one of the members should have username "alice"
    And one of the members should have username "bob"

  Scenario Outline: Get a member by ID
    Given a member exists with username "<username>" and full name "<full_name>"
    When I retrieve the member by their ID
    Then the retrieved member username should be "<username>"
    And the retrieved member full name should be "<full_name>"

    Examples:
      | username | full_name   |
      | charlie  | Charlie Day |
      | dana     | Dana Cruz   |

  Scenario: Fail to list members of a non-existent board
    When I list members of board with ID "nonexistent_board_123"
    Then the request should fail with a 404 error

  Scenario: Fail to get a non-existent member
    When I retrieve a member with ID "nonexistent_member_123"
    Then the request should fail with a 404 error
