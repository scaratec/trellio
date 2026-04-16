Feature: Upload Local Files as Trello Card Attachments

  As a user of the trellio library
  I want to upload local files as attachments to Trello cards
  So that I can attach screenshots, documents, and photos directly

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Upload Board"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "Upload Card"

  # --- Happy Path: Upload with explicit display name ---
  # Persistence validation via independent channel (§4.3):
  # Verify upload result AND confirm via list_attachments.
  # Anti-hardcoding (§2.3): Two different files with different
  # filenames and display names prove the upload generalises.

  Scenario Outline: Upload a local file with an explicit display name
    Given a temporary file "<filename>" with <size_bytes> bytes of content
    When I upload file "<filename>" with name "<display_name>" to the card
    Then the attachment should be created successfully
    And the attachment name should be "<display_name>"
    And listing attachments on the card should include "<display_name>"

    Examples:
      | filename   | size_bytes | display_name     |
      | report.pdf | 2048       | Quarterly Report |
      | photo.jpg  | 4096       | Site Photo       |

  # --- Happy Path: Upload without explicit name ---
  # When no display name is provided, the original filename is used.

  Scenario: Upload a file without explicit name defaults to filename
    Given a temporary file "evidence.png" with 1024 bytes of content
    When I upload file "evidence.png" without a name to the card
    Then the attachment should be created successfully
    And the attachment name should be "evidence.png"
    And listing attachments on the card should include "evidence.png"

  # --- Error Path: File does not exist ---

  Scenario: Reject upload when file does not exist
    When I attempt to upload a non-existent file "/tmp/trellio_nonexistent_abc123.pdf" to the card
    Then the upload should fail with a file-not-found error

  # --- Error Path: Path is a directory ---

  Scenario: Reject upload when path is a directory
    Given a temporary directory "not-a-file"
    When I attempt to upload the directory "not-a-file" to the card
    Then the upload should fail with a not-a-regular-file error

  # --- Error Path: File not readable ---

  Scenario: Reject upload when file has no read permissions
    Given a temporary file "secret.pdf" with 512 bytes of content
    And the file "secret.pdf" has no read permissions
    When I attempt to upload the unreadable file "secret.pdf" to the card
    Then the upload should fail with a permission error
