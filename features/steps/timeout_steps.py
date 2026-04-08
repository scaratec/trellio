from behave import given, when, then
from trellio import TrellioClient, TrelloAPIError
from features.steps.common_steps import run_async
from tests.mock_server import mock_data


@given('a Trellio client with timeout {timeout:g} seconds')
def step_create_client_with_timeout(context, timeout):
    context.client = TrellioClient(
        api_key="valid_api_key",
        token="valid_api_token",
        base_url=context.base_url,
        timeout=timeout,
        initial_delay=0.0,
    )


@given('the server will delay responses by {delay:g} seconds')
def step_set_forced_delay(context, delay):
    mock_data.forced_delay = delay


@when('I attempt to get my member information with timeout')
def step_attempt_get_me_with_timeout(context):
    try:
        context.member_info = run_async(context.client.get_me())
        context.error = None
    except TrelloAPIError as e:
        context.error = e
        context.member_info = None


@when('I get my member information')
def step_get_me(context):
    context.member_info = run_async(context.client.get_me())
    context.error = None


@then('the request should fail with a timeout error')
def step_assert_timeout_error(context):
    assert context.error is not None, "Expected timeout error but request succeeded"
    assert context.error.status_code == 0, f"Expected status 0 for timeout, got {context.error.status_code}"
