from behave import when, then
from trellio import TrellioClient
from features.steps.common_steps import run_async


@when('I use the client as an async context manager with API Key "{api_key}" and Token "{token}"')
def step_use_context_manager(context, api_key, token):
    async def use_client():
        async with TrellioClient(api_key=api_key, token=token, base_url=context.base_url) as client:
            context.member_info = await client.get_me()
            context.error = None
    run_async(use_client())


@when('I create a client with API Key "{api_key}" and Token "{token}" and close it')
def step_create_and_close(context, api_key, token):
    async def create_close():
        client = TrellioClient(api_key=api_key, token=token, base_url=context.base_url)
        await client.get_me()
        await client.close()
        context.client_closed = client._client.is_closed
    run_async(create_close())


@then('the client should be closed')
def step_assert_client_closed(context):
    assert context.client_closed is True
