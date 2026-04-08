from behave import given, when, then
from trellio import TrelloAPIError
from features.steps.common_steps import run_async, capture_api_error


@given('a checklist exists on the card with name "{name}"')
def step_create_existing_checklist(context, name):
    context.existing_checklist = run_async(context.client.create_checklist(context.existing_card.id, name))


@given('a check item exists in the checklist with name "{name}"')
def step_create_existing_check_item(context, name):
    context.existing_check_item = run_async(context.client.create_check_item(context.existing_checklist.id, name))


@when('I create a checklist with name "{name}" on the card')
def step_create_checklist(context, name):
    context.last_checklist = run_async(context.client.create_checklist(context.existing_card.id, name))


@when('I retrieve the checklist by its ID')
def step_get_checklist(context):
    context.retrieved_checklist = run_async(context.client.get_checklist(context.existing_checklist.id))


@when('I list all checklists on the card')
def step_list_card_checklists(context):
    context.checklists_result = run_async(context.client.list_card_checklists(context.existing_card.id))


@then('I should see exactly {count:d} checklists')
def step_assert_checklist_count(context, count):
    assert len(context.checklists_result) == count, f"Expected {count}, got {len(context.checklists_result)}"


@then('one of the checklists should have name "{name}"')
def step_assert_checklist_in_result(context, name):
    names = [cl.name for cl in context.checklists_result]
    assert name in names, f"'{name}' not in {names}"


@when('I delete the checklist')
def step_delete_checklist(context):
    run_async(context.client.delete_checklist(context.existing_checklist.id))


@when('I add a check item with name "{name}" to the checklist')
def step_add_check_item(context, name):
    context.last_check_item = run_async(context.client.create_check_item(context.existing_checklist.id, name))


@when('I update the check item state to "{state}"')
def step_update_check_item_state(context, state):
    context.updated_check_item = run_async(
        context.client.update_check_item(context.existing_card.id, context.existing_check_item.id, state)
    )


@when('I delete the check item')
def step_delete_check_item(context):
    run_async(context.client.delete_check_item(context.existing_checklist.id, context.existing_check_item.id))


@when('I attempt to create a checklist without a name on the card')
def step_attempt_create_checklist_without_name(context):
    capture_api_error(context, context.client.create_checklist(context.existing_card.id, ""))


@when('I retrieve a checklist with ID "{checklist_id}"')
def step_get_checklist_with_explicit_id(context, checklist_id):
    capture_api_error(context, context.client.get_checklist(checklist_id))


@when('I delete a checklist with ID "{checklist_id}"')
def step_delete_checklist_with_explicit_id(context, checklist_id):
    capture_api_error(context, context.client.delete_checklist(checklist_id))


@when('I attempt to create a checklist with name "{name}" on the card')
def step_attempt_create_checklist(context, name):
    capture_api_error(context, context.client.create_checklist(context.existing_card.id, name))


@when('I attempt to retrieve the checklist expecting an error')
def step_attempt_get_checklist(context):
    capture_api_error(context, context.client.get_checklist(context.existing_checklist.id))


@then('the checklist should be created successfully')
def step_assert_checklist_created(context):
    assert context.last_checklist is not None
    assert context.last_checklist.id is not None


@then('the checklist name should be "{name}"')
def step_assert_checklist_name(context, name):
    assert context.last_checklist.name == name


@then('the checklist should belong to the card')
def step_assert_checklist_belongs_to_card(context):
    assert context.last_checklist.id_card == context.existing_card.id


@then('retrieving the checklist by ID should show name "{name}"')
def step_verify_checklist_persisted(context, name):
    checklist = run_async(context.client.get_checklist(context.last_checklist.id))
    assert checklist.name == name


@then('the retrieved checklist name should be "{name}"')
def step_assert_retrieved_checklist_name(context, name):
    assert context.retrieved_checklist.name == name


@then('retrieving the deleted checklist should fail with a 404 error')
def step_verify_checklist_deleted(context):
    try:
        run_async(context.client.get_checklist(context.existing_checklist.id))
        assert False, "Checklist still exists after deletion"
    except TrelloAPIError as e:
        assert e.status_code == 404


@then('the check item should be created successfully')
def step_assert_check_item_created(context):
    assert context.last_check_item is not None
    assert context.last_check_item.id is not None


@then('the check item name should be "{name}"')
def step_assert_check_item_name(context, name):
    assert context.last_check_item.name == name


@then('the check item state should be "{state}"')
def step_assert_check_item_state(context, state):
    assert context.last_check_item.state == state


@then('the check item state should now be "{state}"')
def step_assert_updated_check_item_state(context, state):
    assert context.updated_check_item.state == state


@then('retrieving the checklist should include check item "{name}"')
def step_verify_check_item_in_checklist(context, name):
    checklist = run_async(context.client.get_checklist(context.existing_checklist.id))
    item_names = [ci.name for ci in checklist.check_items]
    assert name in item_names


@then('retrieving the checklist should not include check item "{name}"')
def step_verify_check_item_not_in_checklist(context, name):
    checklist = run_async(context.client.get_checklist(context.existing_checklist.id))
    item_names = [ci.name for ci in checklist.check_items]
    assert name not in item_names
