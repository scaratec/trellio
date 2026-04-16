Feature: Trello Attachments Management

  As a user of the trellio library
  I want to manage URL attachments on Trello cards
  So that I can link external resources to tasks

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Attachments Board"
    And a list exists on that board with name "Work"
    And a card exists in "Work" with name "Attachment Card"

  Scenario Outline: Attach a URL to a card
    When I attach URL "<url>" with name "<name>" to the card
    Then the attachment should be created successfully
    And the attachment name should be "<name>"
    And the attachment URL should be "<url>"
    And listing attachments on the card should include "<name>"

    Examples:
      | url                            | name        |
      | https://example.com/design.pdf | Design Doc  |
      | https://github.com/org/repo    | Source Code |

  Scenario: List attachments on a card
    Given an attachment exists on the card with URL "https://a.com" and name "Link A"
    And an attachment exists on the card with URL "https://b.com" and name "Link B"
    When I list attachments on the card
    Then I should see exactly 2 attachments
    And one of the attachments should have name "Link A"
    And one of the attachments should have name "Link B"

  Scenario: Delete an attachment
    Given an attachment exists on the card with URL "https://temp.com" and name "Temporary"
    When I delete the attachment
    Then listing attachments on the card should not include "Temporary"

  # --- get_attachment ---
  # Anti-hardcoding (§2.3): Two different attachments prove
  # that get returns the correct individual metadata.

  Scenario Outline: Get a single attachment by ID
    Given an attachment exists on the card with URL "<url>" and name "<name>"
    When I get the attachment by its ID
    Then the retrieved attachment name should be "<name>"
    And the retrieved attachment URL should be "<url>"

    Examples:
      | url                            | name        |
      | https://example.com/design.pdf | Design Doc  |
      | https://github.com/org/repo    | Source Code |

  Scenario: Fail to get a non-existent attachment
    When I get attachment with ID "nonexistent_att_123" from the card
    Then the request should fail with a 404 error

  # --- Error paths ---

  Scenario: Fail to attach without a URL
    When I attempt to create an attachment without a URL on the card
    Then the request should fail with a 400 error

  Scenario: Fail to delete a non-existent attachment
    When I delete attachment with ID "nonexistent_attach_123" from the card
    Then the request should fail with a 404 error
