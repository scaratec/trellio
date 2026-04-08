import asyncio
from behave import given, then
from trellio import TrellioClient, TrelloAPIError


def run_async(coro):
    return asyncio.run(coro)


def capture_api_error(context, coro):
    try:
        result = run_async(coro)
        context.error = None
        return result
    except TrelloAPIError as e:
        context.error = e
        return None


@given('a Trellio client with base URL "{url}"')
def step_init_client_with_url(context, url):
    context.base_url = url
    context.api_key = None
    context.token = None


@given('a Trellio client with API Key "{api_key}" and Token "{token}"')
def step_init_client_with_credentials(context, api_key, token):
    context.api_key = api_key
    context.token = token
    context.client = TrellioClient(api_key=api_key, token=token)


@given('the base URL is "{url}"')
def step_override_base_url(context, url):
    context.base_url = url
    context.client.base_url = url


@given('the server will respond with a {status_code:d} error "{message}"')
def step_force_server_error(context, status_code, message):
    context.mock_data.forced_error = {
        "status": status_code,
        "body": {"message": message, "error": "ERROR"}
    }


@then('the request should fail with a {status_code:d} error')
def step_assert_error_status(context, status_code):
    assert context.error is not None, f"Expected error {status_code} but request succeeded"
    assert context.error.status_code == status_code, (
        f"Expected status {status_code}, got {context.error.status_code}"
    )
