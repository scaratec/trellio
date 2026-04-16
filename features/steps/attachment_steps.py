from behave import given, when, then
from features.steps.common_steps import run_async, capture_api_error


@given('an attachment exists on the card with URL "{url}" and name "{name}"')
def step_create_existing_attachment(context, url, name):
    context.existing_attachment = run_async(context.client.create_attachment(context.existing_card.id, url, name))


@when('I attach URL "{url}" with name "{name}" to the card')
def step_create_attachment(context, url, name):
    context.last_attachment = run_async(context.client.create_attachment(context.existing_card.id, url, name))


@when('I list attachments on the card')
def step_list_attachments(context):
    context.attachments = run_async(context.client.list_attachments(context.existing_card.id))


@when('I delete the attachment')
def step_delete_attachment(context):
    run_async(context.client.delete_attachment(context.existing_card.id, context.existing_attachment.id))


@when('I attempt to create an attachment without a URL on the card')
def step_attempt_create_attachment_without_url(context):
    capture_api_error(context, context.client.create_attachment(context.existing_card.id, "", "No URL"))


@when('I attach URL "{url}" to card with ID "{card_id}"')
def step_create_attachment_on_explicit_card(context, url, card_id):
    capture_api_error(context, context.client.create_attachment(card_id, url))


@when('I delete attachment with ID "{attachment_id}" from the card')
def step_delete_attachment_with_explicit_id(context, attachment_id):
    capture_api_error(context, context.client.delete_attachment(context.existing_card.id, attachment_id))


@when('I attempt to attach URL "{url}" to the card expecting an error')
def step_attempt_create_attachment(context, url):
    capture_api_error(context, context.client.create_attachment(context.existing_card.id, url))


@when('I attempt to list attachments on the card expecting an error')
def step_attempt_list_attachments(context):
    capture_api_error(context, context.client.list_attachments(context.existing_card.id))


@then('the attachment should be created successfully')
def step_assert_attachment_created(context):
    assert context.last_attachment is not None
    assert context.last_attachment.id is not None


@then('the attachment name should be "{name}"')
def step_assert_attachment_name(context, name):
    assert context.last_attachment.name == name


@then('the attachment URL should be "{url}"')
def step_assert_attachment_url(context, url):
    assert context.last_attachment.url == url


@then('listing attachments on the card should include "{name}"')
def step_assert_attachment_in_card(context, name):
    attachments = run_async(context.client.list_attachments(context.existing_card.id))
    names = [a.name for a in attachments]
    assert name in names


@then('listing attachments on the card should not include "{name}"')
def step_assert_attachment_not_in_card(context, name):
    attachments = run_async(context.client.list_attachments(context.existing_card.id))
    names = [a.name for a in attachments]
    assert name not in names


@then('I should see exactly {count:d} attachments')
def step_assert_attachment_count(context, count):
    assert len(context.attachments) == count


@then('one of the attachments should have name "{name}"')
def step_assert_attachment_in_list(context, name):
    names = [a.name for a in context.attachments]
    assert name in names


@when('I get the attachment by its ID')
def step_get_attachment_by_id(context):
    context.retrieved_attachment = run_async(
        context.client.get_attachment(context.existing_card.id, context.existing_attachment.id))


@when('I get attachment with ID "{attachment_id}" from the card')
def step_get_attachment_with_explicit_id(context, attachment_id):
    capture_api_error(context, context.client.get_attachment(context.existing_card.id, attachment_id))


@then('the retrieved attachment name should be "{name}"')
def step_assert_retrieved_attachment_name(context, name):
    assert context.retrieved_attachment.name == name, (
        f"Expected name '{name}', got '{context.retrieved_attachment.name}'")


@then('the retrieved attachment URL should be "{url}"')
def step_assert_retrieved_attachment_url(context, url):
    assert context.retrieved_attachment.url == url, (
        f"Expected URL '{url}', got '{context.retrieved_attachment.url}'")
