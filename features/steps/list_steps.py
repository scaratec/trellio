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


@given('a list was created on the board with name "{name}"')
def step_create_named_list(context, name):
    context.last_list = run_async(context.client.create_list(context.existing_board.id, name))


@when('I list all lists on the board')
def step_list_all_lists(context):
    context.lists_result = run_async(context.client.list_lists(context.existing_board.id))


@then('I should see exactly {count:d} lists')
def step_assert_list_count(context, count):
    assert len(context.lists_result) == count, f"Expected {count}, got {len(context.lists_result)}"


@then('one of the lists should have name "{name}"')
def step_assert_list_in_result(context, name):
    names = [l.name for l in context.lists_result]
    assert name in names, f"'{name}' not in {names}"


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


@when('I update the list name to "{new_name}"')
def step_update_list_name(context, new_name):
    context.updated_list = run_async(
        context.client.update_list(context.last_list.id, name=new_name))


@when('I archive the list')
def step_archive_list(context):
    context.updated_list = run_async(
        context.client.update_list(context.last_list.id, closed=True))


@when('I attempt to update list with ID "{list_id}" to name "{name}"')
def step_attempt_update_list(context, list_id, name):
    capture_api_error(context, context.client.update_list(list_id, name=name))


@then('the updated list name should be "{name}"')
def step_assert_updated_list_name(context, name):
    assert context.updated_list.name == name, (
        f"Expected '{name}', got '{context.updated_list.name}'")


@then('retrieving the list by ID should show name "{name}"')
def step_verify_list_persisted(context, name):
    lst = run_async(context.client.get_list(context.last_list.id))
    assert lst.name == name, f"Expected '{name}', got '{lst.name}'"


@then('the list should be archived')
def step_assert_list_archived(context):
    assert context.updated_list.closed is True, (
        f"Expected closed=True, got {context.updated_list.closed}")
