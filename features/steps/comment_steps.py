from behave import given, when, then
from features.steps.common_steps import run_async, capture_api_error


@given('a comment exists on the card with text "{text}"')
def step_create_existing_comment(context, text):
    context.existing_comment = run_async(context.client.add_comment(context.existing_card.id, text))


@when('I add a comment "{text}" to the card')
def step_add_comment(context, text):
    context.last_comment = run_async(context.client.add_comment(context.existing_card.id, text))


@when('I list comments on the card')
def step_list_comments(context):
    context.comments = run_async(context.client.list_comments(context.existing_card.id))


@when('I update the comment text to "{text}"')
def step_update_comment(context, text):
    context.updated_comment = run_async(context.client.update_comment(context.existing_comment.id, text))


@when('I delete the comment')
def step_delete_comment(context):
    run_async(context.client.delete_comment(context.existing_comment.id))


@when('I attempt to add an empty comment to the card')
def step_attempt_add_empty_comment(context):
    capture_api_error(context, context.client.add_comment(context.existing_card.id, ""))


@when('I update a comment with ID "{comment_id}" to text "{text}"')
def step_update_comment_with_explicit_id(context, comment_id, text):
    capture_api_error(context, context.client.update_comment(comment_id, text))


@when('I delete a comment with ID "{comment_id}"')
def step_delete_comment_with_explicit_id(context, comment_id):
    capture_api_error(context, context.client.delete_comment(comment_id))


@when('I attempt to add a comment "{text}" to the card expecting an error')
def step_attempt_add_comment(context, text):
    capture_api_error(context, context.client.add_comment(context.existing_card.id, text))


@when('I attempt to list comments on the card expecting an error')
def step_attempt_list_comments(context):
    capture_api_error(context, context.client.list_comments(context.existing_card.id))


@then('the comment should be created successfully')
def step_assert_comment_created(context):
    assert context.last_comment is not None
    assert context.last_comment.id is not None


@then('the comment text should be "{text}"')
def step_assert_comment_text(context, text):
    assert context.last_comment.text == text


@then('listing comments on the card should include "{text}"')
def step_assert_comment_in_card_comments(context, text):
    comments = run_async(context.client.list_comments(context.existing_card.id))
    texts = [c.text for c in comments]
    assert text in texts, f"'{text}' not in {texts}"


@then('listing comments on the card should not include "{text}"')
def step_assert_comment_not_in_card_comments(context, text):
    comments = run_async(context.client.list_comments(context.existing_card.id))
    texts = [c.text for c in comments]
    assert text not in texts


@then('I should see exactly {count:d} comments')
def step_assert_comment_count(context, count):
    assert len(context.comments) == count


@then('one of the comments should have text "{text}"')
def step_assert_comment_in_list(context, text):
    texts = [c.text for c in context.comments]
    assert text in texts


@then('the comment text should now be "{text}"')
def step_assert_updated_comment_text(context, text):
    assert context.updated_comment.text == text
