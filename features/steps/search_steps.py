from behave import when, then
from features.steps.common_steps import run_async


def _find_board_id_by_name(context, name):
    boards = run_async(context.client.list_boards())
    for b in boards:
        if b.name == name:
            return b.id
    raise AssertionError(f"Board '{name}' not found in created boards")


@when('I search for "{query}"')
def step_search(context, query):
    context.search_result = run_async(context.client.search(query))


@when('I search for "{query}" with limit {limit:d}')
def step_search_with_limit(context, query, limit):
    context.search_result = run_async(context.client.search(query, limit=limit))


@when('I search scoped to board "{board_name}" for "{query}"')
def step_search_scoped_to_board(context, board_name, query):
    board_id = _find_board_id_by_name(context, board_name)
    context.search_result = run_async(
        context.client.search(query, id_boards=board_id)
    )


@then('the search results should contain {count:d} card')
def step_assert_card_count_singular(context, count):
    assert len(context.search_result.cards) == count, (
        f"Expected {count} card, got {len(context.search_result.cards)}"
    )


@then('the only found card should have name "{name}"')
def step_assert_only_card_name(context, name):
    assert len(context.search_result.cards) == 1, (
        f"Expected exactly 1 card, got {len(context.search_result.cards)}"
    )
    assert context.search_result.cards[0].name == name, (
        f"Expected '{name}', got '{context.search_result.cards[0].name}'"
    )


@then('the only found card should have description "{desc}"')
def step_assert_only_card_desc(context, desc):
    assert len(context.search_result.cards) == 1
    actual = context.search_result.cards[0].description or ""
    assert actual == desc, f"Expected desc '{desc}', got '{actual}'"


@then('the only found card should belong to a list named "{list_name}"')
def step_assert_only_card_list(context, list_name):
    assert len(context.search_result.cards) == 1
    list_id = context.search_result.cards[0].id_list
    lst = run_async(context.client.get_list(list_id))
    assert lst.name == list_name, (
        f"Expected list name '{list_name}', got '{lst.name}'"
    )


@then('the search results should contain {count:d} boards')
def step_assert_search_board_count(context, count):
    assert len(context.search_result.boards) == count, (
        f"Expected {count} boards, got {len(context.search_result.boards)}"
    )


@then('the search results should contain {count:d} cards')
def step_assert_search_card_count(context, count):
    assert len(context.search_result.cards) == count, (
        f"Expected {count} cards, got {len(context.search_result.cards)}"
    )


@then('the search results should contain at most {count:d} boards')
def step_assert_search_board_count_at_most(context, count):
    assert len(context.search_result.boards) <= count, (
        f"Expected at most {count} boards, got {len(context.search_result.boards)}"
    )


@then('one of the found boards should have name "{name}"')
def step_assert_found_board_name(context, name):
    names = [b.name for b in context.search_result.boards]
    assert name in names, f"'{name}' not in {names}"


@then('one of the found cards should have name "{name}"')
def step_assert_found_card_name(context, name):
    names = [c.name for c in context.search_result.cards]
    assert name in names, f"'{name}' not in {names}"
