import threading
import http.server
import socketserver
import json
import urllib.parse
import uuid
import time
from behave import fixture, use_fixture

PORT = 3000

class TrelloMockData:
    def __init__(self):
        self.reset()

    def reset(self):
        self.member = {
            "id": "5adde9100465227702830f3a",
            "username": "edgar_bot",
            "fullName": "Edgar Bot",
            "email": "edgar@example.com",
            "initials": "EB",
            "bio": "I am a bot.",
            "url": "https://trello.com/edgar_bot",
            "status": "disconnected",
            "avatarUrl": "https://trello-avatars.s3.amazonaws.com/mock",
            "memberType": "normal",
            "confirmed": True,
            "idPremOrgData": None,
            "nonPublic": {},
            "nonPublicAvailable": False
        }
        self.boards = {}

mock_data = TrelloMockData()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class TrelloMockHandler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_query_params(self):
        parsed_path = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed_path.query)

    def _authenticate(self, query_params):
        key = query_params.get('key', [None])[0]
        token = query_params.get('token', [None])[0]
        if key == "valid_api_key" and token == "valid_api_token":
            return True
        return False

    def do_GET(self):
        params = self._get_query_params()
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path.rstrip('/') # Handle trailing slashes

        if not self._authenticate(params):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"invalid key")
            return

        if path == "/1/members/me":
            self._send_json(mock_data.member)
        elif path == "/1/members/me/boards":
            self._send_json(list(mock_data.boards.values()))
        elif path.startswith("/1/boards/"):
            board_id = path.split("/")[-1]
            if board_id in mock_data.boards:
                self._send_json(mock_data.boards[board_id])
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        params = self._get_query_params()
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path.rstrip('/')

        if not self._authenticate(params):
            self.send_response(401)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = {}
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            # Handle both JSON and form-url-encoded (Trello uses both)
            try:
                post_data = json.loads(body)
            except json.JSONDecodeError:
                post_data = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

        if path == "/1/boards":
            name = post_data.get('name') or params.get('name', [None])[0]
            if not name:
                self.send_response(400)
                self.end_headers()
                return
            
            new_id = str(uuid.uuid4())
            new_board = {
                "id": new_id,
                "name": name,
                "desc": post_data.get('desc', ""),
                "closed": False,
                "url": f"https://trello.com/b/{new_id}/mock"
            }
            mock_data.boards[new_id] = new_board
            self._send_json(new_board)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        params = self._get_query_params()
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path.rstrip('/')

        if not self._authenticate(params):
            self.send_response(401)
            self.end_headers()
            return

        if path.startswith("/1/boards/"):
            board_id = path.split("/")[-1]
            if board_id in mock_data.boards:
                content_length = int(self.headers.get('Content-Length', 0))
                update_data = {}
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
                    update_data = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}
                
                # Merge with query params
                for k, v in params.items():
                    if k not in ["key", "token"]:
                        update_data[k] = v[0]

                mock_data.boards[board_id].update(update_data)
                self._send_json(mock_data.boards[board_id])
            else:
                self.send_response(404)
                self.end_headers()

    def do_DELETE(self):
        params = self._get_query_params()
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path.rstrip('/')

        if not self._authenticate(params):
            self.send_response(401)
            self.end_headers()
            return

        if path.startswith("/1/boards/"):
            board_id = path.split("/")[-1]
            if board_id in mock_data.boards:
                del mock_data.boards[board_id]
                self._send_json({"_value": None}) # Trello often returns null or empty
            else:
                self.send_response(404)
                self.end_headers()

@fixture
def trello_mock_server(context):
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
    mock_data.reset()
