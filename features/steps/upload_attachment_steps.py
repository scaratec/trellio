import os
import tempfile
from behave import given, when, then
from features.steps.common_steps import run_async


def _ensure_temp_dir(context):
    if not hasattr(context, '_temp_dir') or not os.path.isdir(context._temp_dir):
        context._temp_dir = tempfile.mkdtemp()


@given('a temporary file "{filename}" with {size_bytes:d} bytes of content')
def step_create_temp_file(context, filename, size_bytes):
    _ensure_temp_dir(context)
    path = os.path.join(context._temp_dir, filename)
    with open(path, 'wb') as f:
        f.write(os.urandom(size_bytes))
    context.temp_file_path = path


@given('a temporary directory "{dirname}"')
def step_create_temp_directory(context, dirname):
    _ensure_temp_dir(context)
    path = os.path.join(context._temp_dir, dirname)
    os.makedirs(path, exist_ok=True)
    context.temp_dir_path = path


@when('I upload file "{filename}" with name "{display_name}" to the card')
def step_upload_file_with_name(context, filename, display_name):
    path = os.path.join(context._temp_dir, filename)
    context.last_attachment = run_async(
        context.client.upload_attachment(context.existing_card.id, path, name=display_name))


@when('I upload file "{filename}" without a name to the card')
def step_upload_file_without_name(context, filename):
    path = os.path.join(context._temp_dir, filename)
    context.last_attachment = run_async(
        context.client.upload_attachment(context.existing_card.id, path))


@when('I attempt to upload a non-existent file "{file_path}" to the card')
def step_attempt_upload_nonexistent(context, file_path):
    try:
        run_async(context.client.upload_attachment(context.existing_card.id, file_path))
        context.upload_error = None
    except FileNotFoundError as e:
        context.upload_error = e


@when('I attempt to upload the directory "{dirname}" to the card')
def step_attempt_upload_directory(context, dirname):
    path = os.path.join(context._temp_dir, dirname)
    try:
        run_async(context.client.upload_attachment(context.existing_card.id, path))
        context.upload_error = None
    except ValueError as e:
        context.upload_error = e


@then('the upload should fail with a file-not-found error')
def step_assert_file_not_found(context):
    assert context.upload_error is not None, "Expected FileNotFoundError but upload succeeded"
    assert isinstance(context.upload_error, FileNotFoundError), (
        f"Expected FileNotFoundError, got {type(context.upload_error).__name__}")


@then('the upload should fail with a not-a-regular-file error')
def step_assert_not_regular_file(context):
    assert context.upload_error is not None, "Expected ValueError but upload succeeded"
    assert isinstance(context.upload_error, ValueError), (
        f"Expected ValueError, got {type(context.upload_error).__name__}")


@given('the file "{filename}" has no read permissions')
def step_remove_read_permissions(context, filename):
    path = os.path.join(context._temp_dir, filename)
    os.chmod(path, 0o000)


@when('I attempt to upload the unreadable file "{filename}" to the card')
def step_attempt_upload_unreadable(context, filename):
    path = os.path.join(context._temp_dir, filename)
    try:
        run_async(context.client.upload_attachment(context.existing_card.id, path))
        context.upload_error = None
    except PermissionError as e:
        context.upload_error = e


@then('the upload should fail with a permission error')
def step_assert_permission_error(context):
    assert context.upload_error is not None, "Expected PermissionError but upload succeeded"
    assert isinstance(context.upload_error, PermissionError), (
        f"Expected PermissionError, got {type(context.upload_error).__name__}")
