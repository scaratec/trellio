import threading
import time
from behave import fixture, use_fixture
from tests.mock_server import ReusableTCPServer, TrelloMockHandler, PORT, mock_data

@fixture
def trello_mock_server(context):
    """
    Behave fixture to start the mock server in a separate thread before all tests.
    """
    mock_data.reset()
    server = ReusableTCPServer(("127.0.0.1", PORT), TrelloMockHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Wait for server
    for _ in range(20):
        try:
            import socket
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.1):
                break
        except:
            time.sleep(0.05)
    
    context.mock_server = server
    context.mock_data = mock_data
    yield server
    server.shutdown()
    server.server_close()

def before_all(context):
    use_fixture(trello_mock_server, context)

def before_scenario(context, scenario):
    # Ensure a clean state for every scenario
    mock_data.reset()


def after_scenario(context, scenario):
    # Clean up temporary files created during the scenario
    if hasattr(context, '_temp_dir'):
        import shutil
        shutil.rmtree(context._temp_dir, ignore_errors=True)