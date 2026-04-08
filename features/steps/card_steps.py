from behave import given, when, then
from trellio import TrelloAPIError
from features.steps.common_steps import run_async, capture_api_error


@given('a list exists on that board with name "{name}"')
def step_create_existing_list(context, name):
    context.existing_list = run_async(context.client.create_list(context.existing_board.id, name))


@given('a card exists in "{list_name}" with name "{card_name}"')
def step_create_existing_card(context, list_name, card_name):
    if not hasattr(context, 'existing_list') or context.existing_list.name != list_name:
        context.existing_list = run_async(context.client.create_list(context.existing_board.id, list_name))
    context.existing_card = run_async(context.client.create_card(context.existing_list.id, card_name))


@when('I create a new card with name "{card_name}" in the "{list_name}" list')
def step_create_card(context, card_name, list_name):
    assert context.existing_list.name == list_name
    context.last_card = run_async(context.client.create_card(context.existing_list.id, card_name))


@when('I retrieve the card by its ID')
def step_get_card_by_id(context):
    context.retrieved_card = run_async(context.client.get_card(context.existing_card.id))


@when('I update the card name to "{new_name}"')
def step_update_card_name(context, new_name):
    context.updated_card = run_async(context.client.update_card(context.existing_card.id, name=new_name))


@when('I update the card description to "{description}"')
def step_update_card_description(context, description):
    context.updated_card = run_async(context.client.update_card(context.existing_card.id, desc=description))


@when('I delete the card')
def step_delete_card(context):
    run_async(context.client.delete_card(context.existing_card.id))


@when('I attempt to create a card without a name in the "{list_name}" list')
def step_attempt_create_card_without_name(context, list_name):
    assert context.existing_list.name == list_name
    capture_api_error(context, context.client.create_card(context.existing_list.id, ""))


@when('I create a card with name "{name}" in list ID "{list_id}"')
def step_create_card_with_explicit_list_id(context, name, list_id):
    capture_api_error(context, context.client.create_card(list_id, name))


@when('I retrieve a card with ID "{card_id}"')
def step_get_card_with_explicit_id(context, card_id):
    capture_api_error(context, context.client.get_card(card_id))


@when('I update a card with ID "{card_id}" to name "{name}"')
def step_update_card_with_explicit_id(context, card_id, name):
    capture_api_error(context, context.client.update_card(card_id, name=name))


@when('I delete a card with ID "{card_id}"')
def step_delete_card_with_explicit_id(context, card_id):
    capture_api_error(context, context.client.delete_card(card_id))


@then('the card should be created successfully')
def step_assert_card_created(context):
    assert context.last_card is not None
    assert context.last_card.id is not None


@then('the card name should be "{name}"')
def step_assert_card_name(context, name):
    assert context.last_card.name == name


@then('the card should belong to the "{list_name}" list')
def step_assert_card_belongs_to_list(context, list_name):
    assert context.last_card.id_list == context.existing_list.id


@then('the retrieved card name should be "{name}"')
def step_assert_retrieved_card_name(context, name):
    assert context.retrieved_card.name == name


@then('the card name should now be "{name}"')
def step_assert_updated_card_name(context, name):
    assert context.updated_card.name == name


@then('the card description should be "{description}"')
def step_assert_card_description(context, description):
    assert context.updated_card.description == description


@then('retrieving the card by ID should show name "{name}"')
def step_verify_card_persisted(context, name):
    card = run_async(context.client.get_card(context.last_card.id))
    assert card.name == name


@then('retrieving the updated card by ID should show name "{name}"')
def step_verify_updated_card_name_persisted(context, name):
    card = run_async(context.client.get_card(context.existing_card.id))
    assert card.name == name


@then('retrieving the updated card by ID should show description "{desc}"')
def step_verify_updated_card_description_persisted(context, desc):
    card = run_async(context.client.get_card(context.existing_card.id))
    assert card.description == desc


@then('the card should no longer exist')
def step_verify_card_deleted(context):
    try:
        run_async(context.client.get_card(context.existing_card.id))
        assert False, "Card still exists after deletion"
    except TrelloAPIError as e:
        assert e.status_code == 404
