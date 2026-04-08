import http.server
import socketserver
import json
import urllib.parse
import uuid

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
        self.lists = {}
        self.cards = {}
        self.forced_error = None

    def set_member(self, username, full_name, email="test@example.com"):
        self.member["username"] = username
        self.member["fullName"] = full_name
        self.member["email"] = email


mock_data = TrelloMockData()

NOT_FOUND_BODY = {"message": "The requested resource was not found.", "error": "ERROR"}
INVALID_KEY_BODY = {"message": "invalid key", "error": "ERROR"}


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class TrelloMockHandler(http.server.SimpleHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_not_found(self):
        self._send_json(NOT_FOUND_BODY, status=404)

    def _send_invalid_key(self):
        self._send_json(INVALID_KEY_BODY, status=401)

    def _send_bad_request(self, field):
        self._send_json({"message": f"invalid value for {field}", "error": "ERROR"}, status=400)

    def _get_query_params(self):
        parsed_path = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed_path.query)

    def _is_authenticated(self, query_params):
        key = query_params.get('key', [None])[0]
        token = query_params.get('token', [None])[0]
        return key == "valid_api_key" and token == "valid_api_token"

    def _has_forced_error(self):
        if mock_data.forced_error:
            self._send_json(mock_data.forced_error["body"], status=mock_data.forced_error["status"])
            return True
        return False

    def _parse_path(self):
        parsed_path = urllib.parse.urlparse(self.path)
        return parsed_path.path.rstrip('/')

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

    # --- GET ---

    def do_GET(self):
        if self._has_forced_error():
            return
        params = self._get_query_params()
        if not self._is_authenticated(params):
            self._send_invalid_key()
            return
        path = self._parse_path()
        self._route_get(path)

    def _route_get(self, path):
        if path == "/1/members/me":
            self._send_json(mock_data.member)
        elif path == "/1/members/me/boards":
            self._send_json(list(mock_data.boards.values()))
        elif path.startswith("/1/boards/"):
            self._handle_get_board(path)
        elif path.startswith("/1/lists/"):
            self._handle_get_list(path)
        elif path.startswith("/1/cards/"):
            self._handle_get_card(path)
        else:
            self._send_not_found()

    def _handle_get_board(self, path):
        parts = path.split("/")
        board_id = parts[3]
        if len(parts) == 4:
            if board_id in mock_data.boards:
                self._send_json(mock_data.boards[board_id])
            else:
                self._send_not_found()
        elif len(parts) == 5 and parts[4] == "lists":
            if board_id in mock_data.boards:
                board_lists = [l for l in mock_data.lists.values() if l["idBoard"] == board_id]
                self._send_json(board_lists)
            else:
                self._send_not_found()

    def _handle_get_list(self, path):
        parts = path.split("/")
        list_id = parts[3]
        if len(parts) == 4:
            if list_id in mock_data.lists:
                self._send_json(mock_data.lists[list_id])
            else:
                self._send_not_found()
        elif len(parts) == 5 and parts[4] == "cards":
            if list_id in mock_data.lists:
                list_cards = [c for c in mock_data.cards.values() if c["idList"] == list_id]
                self._send_json(list_cards)
            else:
                self._send_not_found()

    def _handle_get_card(self, path):
        card_id = path.split("/")[-1]
        if card_id in mock_data.cards:
            self._send_json(mock_data.cards[card_id])
        else:
            self._send_not_found()

    # --- POST ---

    def do_POST(self):
        if self._has_forced_error():
            return
        params = self._get_query_params()
        if not self._is_authenticated(params):
            self._send_invalid_key()
            return
        path = self._parse_path()
        post_data = self._read_body()
        self._route_post(path, params, post_data)

    def _route_post(self, path, params, post_data):
        if path == "/1/boards":
            self._create_board(params, post_data)
        elif path == "/1/lists":
            self._create_list(params, post_data)
        elif path == "/1/cards":
            self._create_card(params, post_data)
        else:
            self._send_not_found()

    def _create_board(self, params, post_data):
        name = post_data.get('name') or params.get('name', [None])[0]
        if not name:
            self._send_bad_request("name")
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

    def _create_list(self, params, post_data):
        name = post_data.get('name') or params.get('name', [None])[0]
        board_id = post_data.get('idBoard') or params.get('idBoard', [None])[0]
        if not name or not board_id:
            self._send_bad_request("name or idBoard")
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

    def _create_card(self, params, post_data):
        name = post_data.get('name') or params.get('name', [None])[0]
        list_id = post_data.get('idList') or params.get('idList', [None])[0]
        desc = post_data.get('desc') or params.get('desc', [""])[0]
        if not name or not list_id:
            self._send_bad_request("name or idList")
            return
        if list_id not in mock_data.lists:
            self._send_bad_request("idList")
            return
        board_id = mock_data.lists[list_id]["idBoard"]
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
            "badges": {
                "votes": 0,
                "viewingMemberVoted": False,
                "subscribed": False,
                "fogbugz": "",
                "checkItems": 0,
                "checkItemsChecked": 0,
                "comments": 0,
                "attachments": 0,
                "description": False,
                "due": None,
                "dueComplete": False,
            }
        }
        mock_data.cards[new_id] = new_card
        self._send_json(new_card)

    # --- PUT ---

    def do_PUT(self):
        if self._has_forced_error():
            return
        params = self._get_query_params()
        if not self._is_authenticated(params):
            self._send_invalid_key()
            return
        path = self._parse_path()
        update_data = self._read_body()
        for key, values in params.items():
            if key not in ["key", "token"]:
                update_data[key] = values[0]
        self._route_put(path, update_data)

    def _route_put(self, path, update_data):
        if path.startswith("/1/boards/"):
            self._update_board(path, update_data)
        elif path.startswith("/1/cards/"):
            self._update_card(path, update_data)
        else:
            self._send_not_found()

    def _update_board(self, path, update_data):
        board_id = path.split("/")[-1]
        if board_id in mock_data.boards:
            mock_data.boards[board_id].update(update_data)
            self._send_json(mock_data.boards[board_id])
        else:
            self._send_not_found()

    def _update_card(self, path, update_data):
        parts = path.split("/")
        card_id = parts[3]
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        if len(parts) == 4:
            mock_data.cards[card_id].update(update_data)
            self._send_json(mock_data.cards[card_id])
        elif len(parts) == 5:
            field = parts[4]
            if 'value' in update_data:
                mock_data.cards[card_id][field] = update_data['value']
            elif field in update_data:
                mock_data.cards[card_id][field] = update_data[field]
            else:
                self._send_bad_request(field)
                return
            self._send_json(mock_data.cards[card_id])

    # --- DELETE ---

    def do_DELETE(self):
        if self._has_forced_error():
            return
        params = self._get_query_params()
        if not self._is_authenticated(params):
            self._send_invalid_key()
            return
        path = self._parse_path()
        self._route_delete(path)

    def _route_delete(self, path):
        if path.startswith("/1/boards/"):
            self._delete_board(path)
        elif path.startswith("/1/cards/"):
            self._delete_card(path)
        else:
            self._send_not_found()

    def _delete_board(self, path):
        board_id = path.split("/")[-1]
        if board_id in mock_data.boards:
            del mock_data.boards[board_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()

    def _delete_card(self, path):
        card_id = path.split("/")[-1]
        if card_id in mock_data.cards:
            del mock_data.cards[card_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()
