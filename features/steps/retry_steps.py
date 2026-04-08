from behave import given, when
from trellio import TrellioClient
from features.steps.common_steps import run_async, capture_api_error


@given('retry is configured with max retries {max_retries:d} and initial delay {delay:g}')
def step_configure_retry(context, max_retries, delay):
    context.client = TrellioClient(
        api_key=context.api_key,
        token=context.token,
        base_url=context.base_url,
        max_retries=max_retries,
        initial_delay=delay,
    )


@given('the server will respond with a {status_code:d} error "{message}" for {count:d} requests')
def step_force_error_with_countdown(context, status_code, count, message):
    context.mock_data.forced_error = {
        "status": status_code,
        "body": {"message": message, "error": "ERROR"},
        "remaining_count": count,
    }


@given('the server will respond with a {status_code:d} error "{message}" with Retry-After {seconds:g} for {count:d} requests')
def step_force_error_with_retry_after(context, status_code, message, seconds, count):
    context.mock_data.forced_error = {
        "status": status_code,
        "body": {"message": message, "error": "ERROR"},
        "remaining_count": count,
        "headers": {"Retry-After": str(seconds)},
    }


@given('the server will respond with a {status_code:d} error "{message}" permanently')
def step_force_error_permanent(context, status_code, message):
    context.mock_data.forced_error = {
        "status": status_code,
        "body": {"message": message, "error": "ERROR"},
    }


@when('I attempt to list boards with retry')
def step_attempt_list_boards(context):
    capture_api_error(context, context.client.list_boards())
