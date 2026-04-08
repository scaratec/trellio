Feature: Pagination for List Operations

  As a user of the trellio library
  I want to paginate through large result sets
  So that I can handle boards efficiently at scale

  Background:
    Given a Trellio client with API Key "valid_api_key" and Token "valid_api_token"
    And the base URL is "http://127.0.0.1:3000"

  Scenario: List boards with limit returns partial results
    Given 5 boards exist with names "Board A, Board B, Board C, Board D, Board E"
    When I list boards with limit 3
    Then I should receive exactly 3 boards

  Scenario: List boards without limit returns all results
    Given 5 boards exist with names "Board A, Board B, Board C, Board D, Board E"
    When I list all my boards
    Then I should receive exactly 5 boards

  Scenario: Paginate through all boards
    Given 5 boards exist with names "Board A, Board B, Board C, Board D, Board E"
    When I iterate all boards with page size 2
    Then I should have collected exactly 5 boards
    And every created board name should appear in the collected results

  Scenario: Pagination with page size larger than total
    Given 3 boards exist with names "Small A, Small B, Small C"
    When I iterate all boards with page size 10
    Then I should have collected exactly 3 boards
