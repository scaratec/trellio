import logging
from behave import given, then


class CapturingHandler(logging.Handler):

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@given('I am capturing log output from "{logger_name}"')
def step_capture_logs(context, logger_name):
    handler = CapturingHandler()
    target_logger = logging.getLogger(logger_name)
    target_logger.setLevel(logging.DEBUG)
    target_logger.addHandler(handler)
    context.log_capture = handler


@then('the log should contain a DEBUG message matching "{text}"')
def step_assert_debug_log(context, text):
    _assert_log_at_level(context, logging.DEBUG, text)


@then('the log should contain a WARNING message matching "{text}"')
def step_assert_warning_log(context, text):
    _assert_log_at_level(context, logging.WARNING, text)


@then('the log should contain an ERROR message matching "{text}"')
def step_assert_error_log(context, text):
    _assert_log_at_level(context, logging.ERROR, text)


def _assert_log_at_level(context, level, text):
    matching = [
        r for r in context.log_capture.records
        if r.levelno == level and text in r.getMessage()
    ]
    all_messages = [
        f"[{logging.getLevelName(r.levelno)}] {r.getMessage()}"
        for r in context.log_capture.records
    ]
    assert len(matching) > 0, (
        f"No {logging.getLevelName(level)} log matching '{text}'. "
        f"All logs: {all_messages}"
    )
