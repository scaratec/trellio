import asyncio
from behave import given, when, then
from trellio import TrellioClient

# Helper to run async code in sync behave steps
def run_async(coro):
    return asyncio.run(coro)

@given('a Trellio client with base URL "{url}"')
def step_impl(context, url):
    context.base_url = url
    context.api_key = None
    context.token = None

@given('a Trellio client with API Key "{api_key}" and Token "{token}"')
def step_impl(context, api_key, token):
    context.api_key = api_key
    context.token = token
    context.client = TrellioClient(api_key=api_key, token=token)

@given('the base URL is "{url}"')
def step_impl(context, url):
    context.base_url = url
    context.client.base_url = url

@given('I have a valid API Key "{api_key}"')
def step_impl(context, api_key):
    context.api_key = api_key

@given('I have an invalid API Key "{api_key}"')
def step_impl(context, api_key):
    context.api_key = api_key

@given('I have a valid API Token "{token}"')
def step_impl(context, token):
    context.token = token

@when('I check my member information')
def step_impl(context):
    client = TrellioClient(api_key=context.api_key, token=context.token, base_url=context.base_url)
    try:
        context.member_info = run_async(client.get_me())
        context.error = None
    except Exception as e:
        context.error = e
        context.member_info = None

@then('the response should indicate a successful connection')
def step_impl(context):
    assert context.error is None
    assert context.member_info is not None

@then('my username should be "{username}"')
def step_impl(context, username):
    assert context.member_info.username == username

@then('my full name should be "{full_name}"')
def step_impl(context, full_name):
    assert context.member_info.full_name == full_name

@then('the request should fail with a 401 error')
def step_impl(context):
    assert context.error is not None
    # Assuming we raise a specific exception or check the status code in the error
    assert "401" in str(context.error)

@then('the error message should contain "{text}"')
def step_impl(context, text):
    assert text in str(context.error)

# Boards Steps

@when('I create a new board with name "{name}"')
def step_impl(context, name):
    context.last_board = run_async(context.client.create_board(name))

@then('the board should be created successfully')
def step_impl(context):
    assert context.last_board is not None

@then('the board name should be "{name}"')
def step_impl(context, name):
    assert context.last_board.name == name

@then('the board should have a valid ID')
def step_impl(context):
    assert context.last_board.id is not None

@given('a board exists with name "{name}"')
def step_impl(context, name):
    context.existing_board = run_async(context.client.create_board(name))

@when('I list all my boards')
def step_impl(context):
    context.boards = run_async(context.client.list_boards())

@then('I should see at least 1 board')
def step_impl(context):
    assert len(context.boards) >= 1

@then('one of the boards should have name "{name}"')
def step_impl(context, name):
    names = [b.name for b in context.boards]
    assert name in names

@given('I have the ID of that board')
def step_impl(context):
    context.target_board_id = context.existing_board.id

@when('I retrieve the board by its ID')
def step_impl(context):
    context.retrieved_board = run_async(context.client.get_board(context.target_board_id))

@then('the retrieved board name should be "{name}"')
def step_impl(context, name):
    assert context.retrieved_board.name == name

@when('I update the board name to "{new_name}"')
def step_impl(context, new_name):
    context.updated_board = run_async(context.client.update_board(context.target_board_id, name=new_name))

@then('the board name should now be "{name}"')
def step_impl(context, name):
    assert context.updated_board.name == name

@when('I delete the board')
def step_impl(context):
    run_async(context.client.delete_board(context.target_board_id))

@then('the board should no longer exist')
def step_impl(context):
    try:
        run_async(context.client.get_board(context.target_board_id))
        exists = True
    except Exception as e:
        if "404" in str(e):
            exists = False
        else:
            raise e
    assert not exists
