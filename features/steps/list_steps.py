from behave import when, then
from features.steps.common_steps import run_async, capture_api_error


@when('I create a new list with name "{name}" on the board')
def step_create_list(context, name):
    context.last_list = run_async(context.client.create_list(context.existing_board.id, name))


@when('I attempt to create a list without a name on the board')
def step_attempt_create_list_without_name(context):
    capture_api_error(context, context.client.create_list(context.existing_board.id, ""))


@when('I attempt to create a list with name "{name}" without a board ID')
def step_attempt_create_list_without_board(context, name):
    capture_api_error(context, context.client.create_list("", name))


@when('I attempt to create a list with name "{name}" on the board')
def step_attempt_create_list(context, name):
    capture_api_error(context, context.client.create_list(context.existing_board.id, name))


@then('the list should be created successfully')
def step_assert_list_created(context):
    assert context.last_list is not None
    assert context.last_list.id is not None


@then('the list name should be "{name}"')
def step_assert_list_name(context, name):
    assert context.last_list.name == name


@then('the list should belong to the board')
def step_assert_list_belongs_to_board(context):
    assert context.last_list.id_board == context.existing_board.id
