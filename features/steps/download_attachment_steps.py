import os
from behave import given, when, then
from features.steps.common_steps import run_async, capture_api_error
from features.steps.upload_attachment_steps import _ensure_temp_dir


@given('the file "{filename}" was uploaded to the card with name "{display_name}"')
def step_upload_file_to_card(context, filename, display_name):
    path = os.path.join(context._temp_dir, filename)
    context.uploaded_attachment = run_async(
        context.client.upload_attachment(context.existing_card.id, path, name=display_name))


@when('I download the attachment to "{target_filename}"')
def step_download_attachment(context, target_filename):
    _ensure_temp_dir(context)
    target_path = os.path.join(context._temp_dir, target_filename)
    context.downloaded_attachment = run_async(
        context.client.download_attachment(
            context.existing_card.id,
            context.uploaded_attachment.id,
            target_path))
    context.download_target_path = target_path


@when('I attempt to download the attachment to the directory "{dirname}"')
def step_attempt_download_to_directory(context, dirname):
    path = os.path.join(context._temp_dir, dirname)
    try:
        run_async(context.client.download_attachment(
            context.existing_card.id,
            context.existing_attachment.id,
            path))
        context.download_error = None
    except ValueError as e:
        context.download_error = e


@when('I attempt to download the attachment to "{target_path}"')
def step_attempt_download_to_nonexistent_dir(context, target_path):
    try:
        run_async(context.client.download_attachment(
            context.existing_card.id,
            context.existing_attachment.id,
            target_path))
        context.download_error = None
    except FileNotFoundError as e:
        context.download_error = e


@when('I attempt to download attachment "{attachment_id}" from the card')
def step_attempt_download_nonexistent_attachment(context, attachment_id):
    _ensure_temp_dir(context)
    target_path = os.path.join(context._temp_dir, "should_not_exist.bin")
    capture_api_error(context, context.client.download_attachment(
        context.existing_card.id, attachment_id, target_path))


@then('the downloaded file "{target_filename}" should exist')
def step_assert_downloaded_file_exists(context, target_filename):
    path = os.path.join(context._temp_dir, target_filename)
    assert os.path.isfile(path), f"Downloaded file does not exist: {path}"


@then('the downloaded file "{target_filename}" should have {size_bytes:d} bytes')
def step_assert_downloaded_file_size(context, target_filename, size_bytes):
    path = os.path.join(context._temp_dir, target_filename)
    actual = os.path.getsize(path)
    assert actual == size_bytes, f"Expected {size_bytes} bytes, got {actual}"


@then('the download should fail with a not-a-regular-file error')
def step_assert_download_target_is_dir(context):
    assert context.download_error is not None, "Expected ValueError but download succeeded"
    assert isinstance(context.download_error, ValueError), (
        f"Expected ValueError, got {type(context.download_error).__name__}")


@then('the download should fail with a directory-not-found error')
def step_assert_download_dir_not_found(context):
    assert context.download_error is not None, "Expected FileNotFoundError but download succeeded"
    assert isinstance(context.download_error, FileNotFoundError), (
        f"Expected FileNotFoundError, got {type(context.download_error).__name__}")
