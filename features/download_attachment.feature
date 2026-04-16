Feature: Download Trello Card Attachments to Local Files

  As a user of the trellio library
  I want to download Trello card attachments to local files
  So that I can access attached documents offline

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"
    And a board exists with name "Download Board"
    And a list exists on that board with name "Tasks"
    And a card exists in "Tasks" with name "Download Card"

  # --- Happy Path: Round-trip upload then download ---
  # Persistence validation (§4.3): upload a file, then download it
  # and verify the content matches the original.
  # Anti-hardcoding (§2.3): Two different files with different
  # sizes prove the download generalises.

  Scenario Outline: Download an uploaded attachment to a local file
    Given a temporary file "<filename>" with <size_bytes> bytes of content
    And the file "<filename>" was uploaded to the card with name "<display_name>"
    When I download the attachment to "<target_filename>"
    Then the downloaded file "<target_filename>" should exist
    And the downloaded file "<target_filename>" should have <size_bytes> bytes

    Examples:
      | filename   | size_bytes | display_name     | target_filename |
      | report.pdf | 2048       | Quarterly Report | dl_report.pdf   |
      | photo.jpg  | 4096       | Site Photo       | dl_photo.jpg    |

  # --- Error Path: Target path is a directory ---

  Scenario: Reject download when target path is a directory
    Given an attachment exists on the card with URL "https://a.com" and name "Spec"
    And a temporary directory "not-a-file"
    When I attempt to download the attachment to the directory "not-a-file"
    Then the download should fail with a not-a-regular-file error

  # --- Error Path: Target directory does not exist ---

  Scenario: Reject download when target directory does not exist
    Given an attachment exists on the card with URL "https://a.com" and name "Spec"
    When I attempt to download the attachment to "/nonexistent_trellio_path/file.pdf"
    Then the download should fail with a directory-not-found error

  # --- Error Path: Attachment does not exist ---

  Scenario: Reject download for non-existent attachment
    When I attempt to download attachment "nonexistent_att_123" from the card
    Then the request should fail with a 404 error
