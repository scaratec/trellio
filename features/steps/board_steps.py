from behave import given, when, then
from trellio import TrelloAPIError
from features.steps.common_steps import run_async, capture_api_error


@given('a board exists with name "{name}"')
def step_create_existing_board(context, name):
    context.existing_board = run_async(context.client.create_board(name))


@given('I have the ID of that board')
def step_store_board_id(context):
    context.target_board_id = context.existing_board.id


@when('I create a new board with name "{name}"')
def step_create_board(context, name):
    context.last_board = run_async(context.client.create_board(name))


@when('I list all my boards')
def step_list_boards(context):
    context.boards = run_async(context.client.list_boards())


@when('I retrieve the board by its ID')
def step_get_board_by_id(context):
    context.retrieved_board = run_async(context.client.get_board(context.target_board_id))


@when('I update the board name to "{new_name}"')
def step_update_board_name(context, new_name):
    context.updated_board = run_async(context.client.update_board(context.target_board_id, name=new_name))


@when('I delete the board')
def step_delete_board(context):
    run_async(context.client.delete_board(context.target_board_id))


@when('I attempt to create a board with name "{name}"')
def step_attempt_create_board(context, name):
    capture_api_error(context, context.client.create_board(name))


@when('I attempt to create a board without a name')
def step_attempt_create_board_without_name(context):
    capture_api_error(context, context.client.create_board(""))


@when('I retrieve the board by its ID expecting an error')
def step_get_board_expecting_error(context):
    capture_api_error(context, context.client.get_board(context.target_board_id))


@when('I retrieve a board with ID "{board_id}"')
def step_get_board_with_explicit_id(context, board_id):
    capture_api_error(context, context.client.get_board(board_id))


@when('I update a board with ID "{board_id}" to name "{name}"')
def step_update_board_with_explicit_id(context, board_id, name):
    capture_api_error(context, context.client.update_board(board_id, name=name))


@when('I delete a board with ID "{board_id}"')
def step_delete_board_with_explicit_id(context, board_id):
    capture_api_error(context, context.client.delete_board(board_id))


@then('the board should be created successfully')
def step_assert_board_created(context):
    assert context.last_board is not None


@then('the board name should be "{name}"')
def step_assert_board_name(context, name):
    assert context.last_board.name == name


@then('the board should have a valid ID')
def step_assert_board_has_id(context):
    assert context.last_board.id is not None


@then('I should see at least 1 board')
def step_assert_boards_not_empty(context):
    assert len(context.boards) >= 1


@then('one of the boards should have name "{name}"')
def step_assert_board_in_list(context, name):
    board_names = [board.name for board in context.boards]
    assert name in board_names


@then('the retrieved board name should be "{name}"')
def step_assert_retrieved_board_name(context, name):
    assert context.retrieved_board.name == name


@then('the board name should now be "{name}"')
def step_assert_updated_board_name(context, name):
    assert context.updated_board.name == name


@then('retrieving the board by ID should show name "{name}"')
def step_verify_board_persisted(context, name):
    board = run_async(context.client.get_board(context.last_board.id))
    assert board.name == name


@then('retrieving the updated board by ID should show name "{name}"')
def step_verify_updated_board_persisted(context, name):
    board = run_async(context.client.get_board(context.target_board_id))
    assert board.name == name


@then('the board should no longer exist')
def step_verify_board_deleted(context):
    try:
        run_async(context.client.get_board(context.target_board_id))
        assert False, "Board still exists after deletion"
    except TrelloAPIError as e:
        assert e.status_code == 404
