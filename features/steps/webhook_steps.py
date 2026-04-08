from behave import given, when, then
from features.steps.common_steps import run_async, capture_api_error


@given('a webhook exists for the board with callback "{callback}" and description "{desc}"')
def step_create_existing_webhook(context, callback, desc):
    context.existing_webhook = run_async(
        context.client.create_webhook(callback, context.existing_board.id, desc)
    )


@when('I create a webhook for the board with callback "{callback}" and description "{desc}"')
def step_create_webhook(context, callback, desc):
    context.last_webhook = run_async(
        context.client.create_webhook(callback, context.existing_board.id, desc)
    )


@when('I list all webhooks')
def step_list_webhooks(context):
    context.webhooks = run_async(context.client.list_webhooks())


@when('I retrieve the webhook by its ID')
def step_get_webhook(context):
    context.retrieved_webhook = run_async(context.client.get_webhook(context.existing_webhook.id))


@when('I update the webhook description to "{desc}"')
def step_update_webhook_description(context, desc):
    context.updated_webhook = run_async(
        context.client.update_webhook(context.existing_webhook.id, description=desc)
    )


@when('I deactivate the webhook')
def step_deactivate_webhook(context):
    context.updated_webhook = run_async(
        context.client.update_webhook(context.existing_webhook.id, active=False)
    )


@when('I delete the webhook')
def step_delete_webhook(context):
    run_async(context.client.delete_webhook(context.existing_webhook.id))


@when('I attempt to create a webhook without a callback URL for the board')
def step_attempt_create_webhook_without_callback(context):
    capture_api_error(context, context.client.create_webhook("", context.existing_board.id, "No callback"))


@when('I attempt to create a webhook without a model ID')
def step_attempt_create_webhook_without_model(context):
    capture_api_error(context, context.client.create_webhook("https://example.com/hook", "", "No model"))


@when('I retrieve a webhook with ID "{webhook_id}"')
def step_get_webhook_with_explicit_id(context, webhook_id):
    capture_api_error(context, context.client.get_webhook(webhook_id))


@when('I delete a webhook with ID "{webhook_id}"')
def step_delete_webhook_with_explicit_id(context, webhook_id):
    capture_api_error(context, context.client.delete_webhook(webhook_id))


@when('I attempt to create a webhook for the board expecting an error')
def step_attempt_create_webhook(context):
    capture_api_error(context, context.client.create_webhook("https://x.com/hook", context.existing_board.id, "Error"))


@when('I attempt to list webhooks expecting an error')
def step_attempt_list_webhooks(context):
    capture_api_error(context, context.client.list_webhooks())


@then('the webhook should be created successfully')
def step_assert_webhook_created(context):
    assert context.last_webhook is not None
    assert context.last_webhook.id is not None


@then('the webhook callback URL should be "{callback}"')
def step_assert_webhook_callback(context, callback):
    assert context.last_webhook.callback_url == callback


@then('the webhook description should be "{desc}"')
def step_assert_webhook_description(context, desc):
    assert context.last_webhook.description == desc


@then('the webhook should be active')
def step_assert_webhook_active(context):
    assert context.last_webhook.active is True


@then('the webhook should not be active')
def step_assert_webhook_not_active(context):
    assert context.updated_webhook.active is False


@then('retrieving the webhook by ID should show callback "{callback}"')
def step_verify_webhook_callback_persisted(context, callback):
    webhook = run_async(context.client.get_webhook(context.last_webhook.id))
    assert webhook.callback_url == callback


@then('retrieving the webhook by ID should show description "{desc}"')
def step_verify_webhook_description_persisted(context, desc):
    webhook = run_async(context.client.get_webhook(context.existing_webhook.id))
    assert webhook.description == desc


@then('retrieving the webhook by ID should show it as inactive')
def step_verify_webhook_inactive_persisted(context):
    webhook = run_async(context.client.get_webhook(context.existing_webhook.id))
    assert webhook.active is False


@then('the retrieved webhook description should be "{desc}"')
def step_assert_retrieved_webhook_description(context, desc):
    assert context.retrieved_webhook.description == desc


@then('I should see exactly {count:d} webhooks')
def step_assert_webhook_count(context, count):
    assert len(context.webhooks) == count


@then('one of the webhooks should have description "{desc}"')
def step_assert_webhook_in_list(context, desc):
    descriptions = [w.description for w in context.webhooks]
    assert desc in descriptions


@then('the webhook description should now be "{desc}"')
def step_assert_updated_webhook_description(context, desc):
    assert context.updated_webhook.description == desc


@then('listing all webhooks should not include "{desc}"')
def step_assert_webhook_not_in_list(context, desc):
    webhooks = run_async(context.client.list_webhooks())
    descriptions = [w.description for w in webhooks]
    assert desc not in descriptions
