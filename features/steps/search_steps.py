from behave import when, then
from features.steps.common_steps import run_async


@when('I search for "{query}"')
def step_search(context, query):
    context.search_result = run_async(context.client.search(query))


@when('I search for "{query}" with limit {limit:d}')
def step_search_with_limit(context, query, limit):
    context.search_result = run_async(context.client.search(query, limit=limit))


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
