Feature: Trello Webhooks Registration

  As a user of the trellio library
  I want to manage webhook registrations
  So that I can receive notifications about Trello changes

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario Outline: Create a webhook
    Given a board exists with name "<board_name>"
    When I create a webhook for the board with callback "<callback>" and description "<desc>"
    Then the webhook should be created successfully
    And the webhook callback URL should be "<callback>"
    And the webhook description should be "<desc>"
    And the webhook should be active
    And retrieving the webhook by ID should show callback "<callback>"

    Examples:
      | board_name    | callback                 | desc           |
      | Webhook Board | https://myapp.com/hook   | Board updates  |
      | Events Board  | https://myapp.com/events | Event listener |

  Scenario: List all webhooks
    Given a board exists with name "List Hooks Board"
    And a webhook exists for the board with callback "https://a.com/hook" and description "Hook A"
    And a webhook exists for the board with callback "https://b.com/hook" and description "Hook B"
    When I list all webhooks
    Then I should see exactly 2 webhooks
    And one of the webhooks should have description "Hook A"
    And one of the webhooks should have description "Hook B"

  Scenario: Get a specific webhook
    Given a board exists with name "Get Hook Board"
    And a webhook exists for the board with callback "https://get.com/hook" and description "Get Hook"
    When I retrieve the webhook by its ID
    Then the retrieved webhook description should be "Get Hook"

  Scenario Outline: Update a webhook
    Given a board exists with name "Update Hook Board"
    And a webhook exists for the board with callback "https://old.com/hook" and description "<old_desc>"
    When I update the webhook description to "<new_desc>"
    Then the webhook description should now be "<new_desc>"
    And retrieving the webhook by ID should show description "<new_desc>"

    Examples:
      | old_desc       | new_desc        |
      | Old descriptor | New descriptor  |
      | Alpha hook     | Production hook |

  Scenario: Deactivate a webhook
    Given a board exists with name "Deactivate Board"
    And a webhook exists for the board with callback "https://deactivate.com/hook" and description "Toggle"
    When I deactivate the webhook
    Then the webhook should not be active

  Scenario: Delete a webhook
    Given a board exists with name "Delete Hook Board"
    And a webhook exists for the board with callback "https://delete.com/hook" and description "Delete Me"
    When I delete the webhook
    Then listing all webhooks should not include "Delete Me"

  Scenario: Fail to create a webhook without a callback URL
    Given a board exists with name "No Callback Board"
    When I attempt to create a webhook without a callback URL for the board
    Then the request should fail with a 400 error

  Scenario: Fail to create a webhook without a model ID
    When I attempt to create a webhook without a model ID
    Then the request should fail with a 400 error

  Scenario: Fail to get a non-existent webhook
    When I retrieve a webhook with ID "nonexistent_webhook_123"
    Then the request should fail with a 404 error

  Scenario: Fail to delete a non-existent webhook
    When I delete a webhook with ID "nonexistent_webhook_123"
    Then the request should fail with a 404 error
