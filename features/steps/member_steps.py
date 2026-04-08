from behave import given, when, then
import uuid
from features.steps.common_steps import run_async, capture_api_error
from tests.mock_server import mock_data


@given('the board has a member with username "{username}" and full name "{full_name}"')
def step_add_board_member(context, username, full_name):
    member_id = str(uuid.uuid4())
    mock_data.members[member_id] = {
        "id": member_id,
        "username": username,
        "fullName": full_name,
        "email": f"{username}@example.com",
        "url": f"https://trello.com/{username}",
    }
    board_id = context.existing_board.id
    if board_id not in mock_data.board_members:
        mock_data.board_members[board_id] = []
    mock_data.board_members[board_id].append(member_id)


@given('a member exists with username "{username}" and full name "{full_name}"')
def step_create_member(context, username, full_name):
    member_id = str(uuid.uuid4())
    mock_data.members[member_id] = {
        "id": member_id,
        "username": username,
        "fullName": full_name,
        "email": f"{username}@example.com",
        "url": f"https://trello.com/{username}",
    }
    context.existing_member_id = member_id


@when('I list members of the board')
def step_list_board_members(context):
    context.members = run_async(context.client.list_board_members(context.existing_board.id))


@when('I retrieve the member by their ID')
def step_get_member(context):
    context.retrieved_member = run_async(context.client.get_member(context.existing_member_id))


@when('I list members of board with ID "{board_id}"')
def step_list_members_with_explicit_id(context, board_id):
    capture_api_error(context, context.client.list_board_members(board_id))


@when('I retrieve a member with ID "{member_id}"')
def step_get_member_with_explicit_id(context, member_id):
    capture_api_error(context, context.client.get_member(member_id))


@then('I should see exactly {count:d} members')
def step_assert_member_count(context, count):
    assert len(context.members) == count


@then('one of the members should have username "{username}"')
def step_assert_member_in_list(context, username):
    usernames = [m.username for m in context.members]
    assert username in usernames


@then('the retrieved member username should be "{username}"')
def step_assert_retrieved_member_username(context, username):
    assert context.retrieved_member.username == username


@then('the retrieved member full name should be "{full_name}"')
def step_assert_retrieved_member_full_name(context, full_name):
    assert context.retrieved_member.full_name == full_name
