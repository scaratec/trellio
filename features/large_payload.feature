Feature: Large Payload Handling

  As a user of the trellio library
  I want to update cards with large descriptions and add long comments
  So that I can store detailed documentation on Trello cards

  The Trello API allows descriptions up to 16384 characters.
  The client must send large payloads in the HTTP request body,
  not as URL query parameters, to avoid CloudFront's URI length
  limit (~8 KiB). The mock server enforces this limit (§7.2).

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Payload Board"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "Large Card"

  # --- update_card with large description ---
  # Anti-hardcoding (§2.3): Two different lengths prove the fix
  # is not length-specific. Persistence validation (§4.3):
  # verify via get_card.

  Scenario Outline: Update a card with a large description
    When I update the card description to a string of <length> characters
    Then the update should succeed
    And retrieving the card should show a description of <length> characters

    Examples:
      | length |
      | 8000   |
      | 15000  |

  # --- create_card with large description ---

  Scenario: Create a card with a large description
    When I create a card with name "Detailed" and a description of 10000 characters in the list
    Then the card should be created successfully
    And retrieving the created card should show a description of 10000 characters

  # --- add_comment with large text ---

  Scenario: Add a long comment to a card
    When I add a comment of 8000 characters to the card
    Then the comment should be added successfully
