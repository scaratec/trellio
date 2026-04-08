from behave import given, when, then
from features.steps.common_steps import run_async, capture_api_error


@given('a label exists on the board with name "{name}" and color "{color}"')
def step_create_existing_label(context, name, color):
    context.existing_label = run_async(context.client.create_label(name, color, context.existing_board.id))


@when('I create a label with name "{name}" and color "{color}" on the board')
def step_create_label(context, name, color):
    context.last_label = run_async(context.client.create_label(name, color, context.existing_board.id))


@when('I list labels on the board')
def step_list_labels(context):
    context.labels = run_async(context.client.list_board_labels(context.existing_board.id))


@when('I update the label name to "{new_name}"')
def step_update_label_name(context, new_name):
    context.updated_label = run_async(context.client.update_label(context.existing_label.id, name=new_name))


@when('I update the label color to "{new_color}"')
def step_update_label_color(context, new_color):
    context.updated_label = run_async(context.client.update_label(context.existing_label.id, color=new_color))


@when('I delete the label')
def step_delete_label(context):
    run_async(context.client.delete_label(context.existing_label.id))


@when('I attempt to create a label without a name on the board')
def step_attempt_create_label_without_name(context):
    capture_api_error(context, context.client.create_label("", "red", context.existing_board.id))


@when('I update a label with ID "{label_id}" to name "{name}"')
def step_update_label_with_explicit_id(context, label_id, name):
    capture_api_error(context, context.client.update_label(label_id, name=name))


@when('I delete a label with ID "{label_id}"')
def step_delete_label_with_explicit_id(context, label_id):
    capture_api_error(context, context.client.delete_label(label_id))


@when('I attempt to create a label with name "{name}" and color "{color}" on the board')
def step_attempt_create_label(context, name, color):
    capture_api_error(context, context.client.create_label(name, color, context.existing_board.id))


@when('I attempt to list labels on the board expecting an error')
def step_attempt_list_labels(context):
    capture_api_error(context, context.client.list_board_labels(context.existing_board.id))


@then('the label should be created successfully')
def step_assert_label_created(context):
    assert context.last_label is not None
    assert context.last_label.id is not None


@then('the label name should be "{name}"')
def step_assert_label_name(context, name):
    assert context.last_label.name == name


@then('the label color should be "{color}"')
def step_assert_label_color(context, color):
    assert context.last_label.color == color


@then('the label should belong to the board')
def step_assert_label_belongs_to_board(context):
    assert context.last_label.id_board == context.existing_board.id


@then('listing labels on the board should include "{name}"')
def step_assert_label_in_board_labels(context, name):
    labels = run_async(context.client.list_board_labels(context.existing_board.id))
    label_names = [l.name for l in labels]
    assert name in label_names, f"'{name}' not in {label_names}"


@then('listing labels on the board should not include "{name}"')
def step_assert_label_not_in_board_labels(context, name):
    labels = run_async(context.client.list_board_labels(context.existing_board.id))
    label_names = [l.name for l in labels]
    assert name not in label_names


@then('I should see exactly {count:d} labels')
def step_assert_label_count(context, count):
    assert len(context.labels) == count


@then('one of the labels should have name "{name}"')
def step_assert_label_in_list(context, name):
    label_names = [l.name for l in context.labels]
    assert name in label_names


@then('the label name should now be "{name}"')
def step_assert_updated_label_name(context, name):
    assert context.updated_label.name == name


@then('the label color should now be "{color}"')
def step_assert_updated_label_color(context, color):
    assert context.updated_label.color == color
