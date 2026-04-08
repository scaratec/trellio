from behave import given, when, then
from trellio import TrellioClient, TrelloAPIError
from features.steps.common_steps import run_async


@given('the mock member has username "{username}" and full name "{full_name}"')
def step_configure_mock_member(context, username, full_name):
    context.mock_data.set_member(username=username, full_name=full_name)


@given('I have a valid API Key "{api_key}"')
def step_set_valid_api_key(context, api_key):
    context.api_key = api_key


@given('I have an invalid API Key "{api_key}"')
def step_set_invalid_api_key(context, api_key):
    context.api_key = api_key


@given('I have a valid API Token "{token}"')
def step_set_valid_token(context, token):
    context.token = token


@given('I have an empty API Key')
def step_set_empty_api_key(context):
    context.api_key = ""


@given('I have an empty API Token')
def step_set_empty_token(context):
    context.token = ""


def _check_member_info(context):
    client = TrellioClient(api_key=context.api_key, token=context.token, base_url=context.base_url)
    try:
        context.member_info = run_async(client.get_me())
        context.error = None
    except TrelloAPIError as e:
        context.error = e
        context.member_info = None


@when('I check my member information')
def step_check_member_info(context):
    _check_member_info(context)


@when('I check my member information with no API key')
def step_check_member_info_without_key(context):
    context.api_key = ""
    _check_member_info(context)


@then('the response should indicate a successful connection')
def step_assert_successful_connection(context):
    assert context.error is None
    assert context.member_info is not None


@then('my username should be "{username}"')
def step_assert_username(context, username):
    assert context.member_info.username == username


@then('my full name should be "{full_name}"')
def step_assert_full_name(context, full_name):
    assert context.member_info.full_name == full_name


@then('the error message should contain "{text}"')
def step_assert_error_message_contains(context, text):
    assert text in str(context.error)
