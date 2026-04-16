from behave import when, then
from features.steps.common_steps import run_async


def _make_text(length):
    """Generate a deterministic string of exactly `length` characters."""
    base = "Lorem ipsum dolor sit amet. "
    repeated = base * ((length // len(base)) + 1)
    return repeated[:length]


@when('I update the card description to a string of {length:d} characters')
def step_update_card_large_desc(context, length):
    text = _make_text(length)
    context.large_desc = text
    context.updated_card = run_async(
        context.client.update_card(context.existing_card.id, desc=text))


@then('the update should succeed')
def step_assert_update_succeeded(context):
    assert context.updated_card is not None
    assert context.updated_card.id is not None


@then('retrieving the card should show a description of {length:d} characters')
def step_verify_card_desc_length(context, length):
    card = run_async(context.client.get_card(context.existing_card.id))
    actual = len(card.description)
    assert actual == length, (
        f"Expected description of {length} chars, got {actual}")


@when('I create a card with name "{name}" and a description of {length:d} characters in the list')
def step_create_card_large_desc(context, name, length):
    text = _make_text(length)
    context.large_desc = text
    context.last_card = run_async(
        context.client.create_card(context.existing_list.id, name, desc=text))


@then('retrieving the created card should show a description of {length:d} characters')
def step_verify_created_card_desc_length(context, length):
    card = run_async(context.client.get_card(context.last_card.id))
    actual = len(card.description)
    assert actual == length, (
        f"Expected description of {length} chars, got {actual}")


@when('I add a comment of {length:d} characters to the card')
def step_add_large_comment(context, length):
    text = _make_text(length)
    context.last_comment = run_async(
        context.client.add_comment(context.existing_card.id, text))


@then('the comment should be added successfully')
def step_assert_comment_added(context):
    assert context.last_comment is not None
    assert context.last_comment.id is not None
