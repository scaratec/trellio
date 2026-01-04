import http.server
import socketserver
import json
import urllib.parse
import uuid

PORT = 3000

class TrelloMockData:
    """
    In-memory data store for the Mock Server.
    Resets before each scenario to ensure test isolation.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the mock data to its initial state."""
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
        self.lists = {}
        self.cards = {}

# Global instance to hold the state
mock_data = TrelloMockData()

class ReusableTCPServer(socketserver.TCPServer):
    """TCP Server that allows address reuse to avoid 'Address already in use' errors during tests."""
    allow_reuse_address = True

class TrelloMockHandler(http.server.SimpleHTTPRequestHandler):
    """
    Request Handler that simulates Trello API endpoints.
    Validates API Key/Token and performs CRUD operations on the in-memory data.
    """
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_query_params(self):
        parsed_path = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed_path.query)

    def _authenticate(self, query_params):
        """Simple check for hardcoded test credentials."""
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
            # Could be /1/boards/{id} or /1/boards/{id}/lists
            parts = path.split("/")
            board_id = parts[3]
            
            if len(parts) == 4: # /1/boards/{id}
                if board_id in mock_data.boards:
                    self._send_json(mock_data.boards[board_id])
                else:
                    self.send_response(404)
                    self.end_headers()
            elif len(parts) == 5 and parts[4] == "lists": # /1/boards/{id}/lists
                if board_id in mock_data.boards:
                    board_lists = [l for l in mock_data.lists.values() if l["idBoard"] == board_id]
                    self._send_json(board_lists)
                else:
                    self.send_response(404)
                    self.end_headers()
        elif path.startswith("/1/lists/"):
            # /1/lists/{id} or /1/lists/{id}/cards
            parts = path.split("/")
            list_id = parts[3]
            
            if len(parts) == 4:
                if list_id in mock_data.lists:
                    self._send_json(mock_data.lists[list_id])
                else:
                    self.send_response(404)
                    self.end_headers()
            elif len(parts) == 5 and parts[4] == "cards":
                 if list_id in mock_data.lists:
                    list_cards = [c for c in mock_data.cards.values() if c["idList"] == list_id]
                    self._send_json(list_cards)
                 else:
                    self.send_response(404)
                    self.end_headers()

        elif path.startswith("/1/cards/"):
            card_id = path.split("/")[-1]
            if card_id in mock_data.cards:
                self._send_json(mock_data.cards[card_id])
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
            # Handle both JSON and form-url-encoded
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
            
        elif path == "/1/lists":
            name = post_data.get('name') or params.get('name', [None])[0]
            board_id = post_data.get('idBoard') or params.get('idBoard', [None])[0]
            
            if not name or not board_id:
                self.send_response(400)
                self.end_headers()
                return
                
            new_id = str(uuid.uuid4())
            new_list = {
                "id": new_id,
                "name": name,
                "idBoard": board_id,
                "closed": False,
                "pos": 0
            }
            mock_data.lists[new_id] = new_list
            self._send_json(new_list)

        elif path == "/1/cards":
            name = post_data.get('name') or params.get('name', [None])[0]
            list_id = post_data.get('idList') or params.get('idList', [None])[0]
            desc = post_data.get('desc') or params.get('desc', [""])[0]
            
            if not name or not list_id:
                self.send_response(400)
                self.end_headers()
                return
            
            # Find the board ID from the list
            board_id = mock_data.lists[list_id]["idBoard"] if list_id in mock_data.lists else None

            new_id = str(uuid.uuid4())
            new_card = {
                "id": new_id,
                "name": name,
                "idList": list_id,
                "idBoard": board_id,
                "desc": desc,
                "pos": "top",
                "closed": False,
                "url": f"https://trello.com/c/{new_id}/mock",
                "shortUrl": f"https://trello.com/c/{new_id}",
                "due": None,
                "dueComplete": False,
                "dateLastActivity": "2023-01-01T00:00:00.000Z",
                "idMembers": [],
                "idLabels": [],
                "idChecklists": [],
                "idShort": 1,
                "labels": [],
                "badges": { "votes": 0, "viewingMemberVoted": False, "subscribed": False, "fogbugz": "", "checkItems": 0, "checkItemsChecked": 0, "comments": 0, "attachments": 0, "description": False, "due": None, "dueComplete": False}
            }
            mock_data.cards[new_id] = new_card
            self._send_json(new_card)
            
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
        
        content_length = int(self.headers.get('Content-Length', 0))
        update_data = {}
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                update_data = json.loads(body)
            except json.JSONDecodeError:
                update_data = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}
        
        # Merge with query params
        for k, v in params.items():
            if k not in ["key", "token"]:
                update_data[k] = v[0]

        if path.startswith("/1/boards/"):
            board_id = path.split("/")[-1]
            if board_id in mock_data.boards:
                mock_data.boards[board_id].update(update_data)
                self._send_json(mock_data.boards[board_id])
            else:
                self.send_response(404)
                self.end_headers()
        
        elif path.startswith("/1/cards/"):
            parts = path.split("/")
            card_id = parts[3]
            
            if card_id in mock_data.cards:
                if len(parts) == 4: # /1/cards/{id}
                    mock_data.cards[card_id].update(update_data)
                    self._send_json(mock_data.cards[card_id])
                elif len(parts) == 5: # /1/cards/{id}/{field}
                    field = parts[4]
                    # Trello typically accepts {value: 'new value'} for specific fields
                    # But py-trello might send it differently. update_data has the merged params.
                    if 'value' in update_data:
                         mock_data.cards[card_id][field] = update_data['value']
                         self._send_json(mock_data.cards[card_id])
                    else:
                        # Fallback if value is not explicit, might be implicit from query param with same name as field?
                        # Actually py-trello sends query params: value=NewName
                        pass
                        # For now, assume update_data contains 'value' because we merged query params
                        if 'value' in update_data:
                             mock_data.cards[card_id][field] = update_data['value']
                             self._send_json(mock_data.cards[card_id])
                        else:
                             # Some fields might be updated directly if the body keys match?
                             # But this endpoint specific logic usually implies 'value' param.
                             # Let's check if the field itself is in update_data (rare for this endpoint style)
                             if field in update_data:
                                 mock_data.cards[card_id][field] = update_data[field]
                                 self._send_json(mock_data.cards[card_id])
                             else:
                                 self.send_response(400)
                                 self.end_headers()

            else:
                self.send_response(404)
                self.end_headers()
        
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
                self._send_json({"_value": None}) 
            else:
                self.send_response(404)
                self.end_headers()
        
        elif path.startswith("/1/cards/"):
            card_id = path.split("/")[-1]
            if card_id in mock_data.cards:
                del mock_data.cards[card_id]
                self._send_json({"_value": None})
            else:
                self.send_response(404)
                self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()
