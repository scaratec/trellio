from behave import given, when, then
from features.steps.common_steps import run_async


@given('{count:d} boards exist with names "{csv_names}"')
def step_create_multiple_boards(context, count, csv_names):
    names = [n.strip() for n in csv_names.split(",")]
    assert len(names) == count, f"Expected {count} names, got {len(names)}"
    context.created_board_names = []
    for name in names:
        run_async(context.client.create_board(name))
        context.created_board_names.append(name)


@when('I list boards with limit {limit:d}')
def step_list_boards_with_limit(context, limit):
    context.boards = run_async(context.client.list_boards(limit=limit))


@when('I iterate all boards with page size {page_size:d}')
def step_iterate_all_boards(context, page_size):
    async def collect():
        results = []
        async for board in context.client.list_all_boards(page_size=page_size):
            results.append(board)
        return results
    context.collected_boards = run_async(collect())


@then('I should receive exactly {count:d} boards')
def step_assert_board_count(context, count):
    assert len(context.boards) == count, (
        f"Expected {count} boards, got {len(context.boards)}"
    )


@then('I should have collected exactly {count:d} boards')
def step_assert_collected_board_count(context, count):
    assert len(context.collected_boards) == count, (
        f"Expected {count} boards, got {len(context.collected_boards)}"
    )


@then('every created board name should appear in the collected results')
def step_assert_all_created_boards_collected(context):
    collected_names = [b.name for b in context.collected_boards]
    for name in context.created_board_names:
        assert name in collected_names, f"Board '{name}' not in collected results"
