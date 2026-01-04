import pytest
import threading
import time
import json
import urllib.parse
from trello import TrelloClient
from features.environment import ReusableTCPServer, TrelloMockHandler, PORT, mock_data

@pytest.fixture(scope="module", autouse=True)
def mock_server():
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
            
    yield server
    server.shutdown()
    server.server_close()

def test_pytrello_authentication(monkeypatch):
    # py-trello uses the API Key and Token
    client = TrelloClient(
        api_key='valid_api_key',
        token='valid_api_token'
    )
    
    import trello.trelloclient
    def mock_fetch_json(self, uri_path, http_method='GET', headers=None, query_params=None, post_args=None, files=None):
        if query_params is None: query_params = {}
        if uri_path[0] == '/':
            uri_path = uri_path[1:]
        
        # Use resource_owner_key for token as identified in py-trello source
        token = self.resource_owner_key
        api_key = self.api_key
        
        query_params['key'] = api_key
        query_params['token'] = token
        
        # Properly merge query params
        parsed_uri = urllib.parse.urlparse(uri_path)
        existing_params = urllib.parse.parse_qs(parsed_uri.query)
        for k, v in existing_params.items():
            if k not in query_params:
                query_params[k] = v[0]
        
        clean_path = parsed_uri.path
        qs = urllib.parse.urlencode(query_params)
        url = f"http://127.0.0.1:{PORT}/1/{clean_path}?{qs}"
            
        response = self.http_service.request(http_method, url,
                                             headers=headers, data=json.dumps(post_args) if post_args else None,
                                             files=files,
                                             proxies=self.proxies)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            return response.json()

    monkeypatch.setattr(trello.trelloclient.TrelloClient, "fetch_json", mock_fetch_json)
    
    info = client.get_member('me')
    assert info.username == "edgar_bot"
    assert info.full_name == "Edgar Bot"

def test_pytrello_boards(monkeypatch):
    client = TrelloClient(
        api_key='valid_api_key',
        token='valid_api_token'
    )
    
    import trello.trelloclient
    def mock_fetch_json(self, uri_path, http_method='GET', headers=None, query_params=None, post_args=None, files=None):
        if query_params is None: query_params = {}
        if uri_path[0] == '/':
            uri_path = uri_path[1:]
            
        token = self.resource_owner_key
        api_key = self.api_key
            
        query_params['key'] = api_key
        query_params['token'] = token
            
        # Properly merge query params
        parsed_uri = urllib.parse.urlparse(uri_path)
        existing_params = urllib.parse.parse_qs(parsed_uri.query)
        for k, v in existing_params.items():
            if k not in query_params:
                query_params[k] = v[0]
        
        clean_path = parsed_uri.path
        qs = urllib.parse.urlencode(query_params)
        url = f"http://127.0.0.1:{PORT}/1/{clean_path}?{qs}"
        
        response = self.http_service.request(http_method, url,
                                             headers=headers, data=json.dumps(post_args) if post_args else None,
                                             files=files,
                                             proxies=self.proxies)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            return response.json()
    
    monkeypatch.setattr(trello.trelloclient.TrelloClient, "fetch_json", mock_fetch_json)
    
    # Create board
    new_board = client.add_board("Test Board")
    assert new_board.name == "Test Board"
    
    # List boards
    boards = client.list_boards()
    assert len(boards) == 1
    assert boards[0].name == "Test Board"
    
    # Get board
    retrieved_board = client.get_board(new_board.id)
    assert retrieved_board.name == "Test Board"
