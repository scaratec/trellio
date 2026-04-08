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
        self.labels = {}
        self.checklists = {}
        self.check_items = {}
        self.comments = {}
        self.members = {}
        self.board_members = {}
        self.attachments = {}
        self.webhooks = {}
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
            remaining = mock_data.forced_error.get("remaining_count")
            if remaining is not None:
                mock_data.forced_error["remaining_count"] = remaining - 1
                if mock_data.forced_error["remaining_count"] <= 0:
                    mock_data.forced_error = None
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
        self._route_get(path, params)

    def _route_get(self, path, params=None):
        if path == "/1/members/me":
            self._send_json(mock_data.member)
        elif path == "/1/members/me/boards":
            self._handle_list_boards(params or {})
        elif path.startswith("/1/boards/"):
            self._handle_get_board(path)
        elif path.startswith("/1/lists/"):
            self._handle_get_list(path)
        elif path.startswith("/1/cards/"):
            self._handle_get_card(path, params or {})
        elif path.startswith("/1/checklists/"):
            self._handle_get_checklist(path)
        elif path == "/1/webhooks":
            self._send_json(list(mock_data.webhooks.values()))
        elif path.startswith("/1/webhooks/"):
            self._handle_get_webhook(path)
        elif path.startswith("/1/members/"):
            self._handle_get_member(path)
        elif path.startswith("/1/labels/"):
            self._handle_get_label(path)
        else:
            self._send_not_found()

    def _handle_list_boards(self, params):
        boards = list(mock_data.boards.values())
        since = params.get('since', [None])[0]
        if since:
            board_ids = list(mock_data.boards.keys())
            if since in board_ids:
                start = board_ids.index(since) + 1
                boards = [mock_data.boards[bid] for bid in board_ids[start:]]
            else:
                boards = []
        limit = params.get('limit', [None])[0]
        if limit is not None:
            boards = boards[:int(limit)]
        self._send_json(boards)

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
        elif len(parts) == 5 and parts[4] == "labels":
            if board_id in mock_data.boards:
                board_labels = [l for l in mock_data.labels.values() if l["idBoard"] == board_id]
                self._send_json(board_labels)
            else:
                self._send_not_found()
        elif len(parts) == 5 and parts[4] == "members":
            if board_id in mock_data.boards:
                member_ids = mock_data.board_members.get(board_id, [])
                members = [mock_data.members[mid] for mid in member_ids if mid in mock_data.members]
                self._send_json(members)
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

    def _handle_get_card(self, path, params=None):
        parts = path.split("/")
        card_id = parts[3]
        if len(parts) == 4:
            if card_id in mock_data.cards:
                self._send_json(mock_data.cards[card_id])
            else:
                self._send_not_found()
        elif len(parts) == 5 and parts[4] == "actions":
            self._handle_get_card_comments(card_id, params or {})
        elif len(parts) == 5 and parts[4] == "attachments":
            self._handle_get_card_attachments(card_id)
        else:
            self._send_not_found()

    def _handle_get_card_comments(self, card_id, params):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        filter_value = params.get('filter', [None])[0]
        if filter_value == "commentCard":
            card_comments = [c for c in mock_data.comments.values() if c["idCard"] == card_id]
            self._send_json(card_comments)
        else:
            self._send_json([])

    def _handle_get_card_attachments(self, card_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        card_attachments = [a for a in mock_data.attachments.values() if a["idCard"] == card_id]
        self._send_json(card_attachments)

    def _handle_get_checklist(self, path):
        parts = path.split("/")
        checklist_id = parts[3]
        if checklist_id in mock_data.checklists:
            checklist = dict(mock_data.checklists[checklist_id])
            checklist["checkItems"] = [
                ci for ci in mock_data.check_items.values()
                if ci["idChecklist"] == checklist_id
            ]
            self._send_json(checklist)
        else:
            self._send_not_found()

    def _handle_get_webhook(self, path):
        webhook_id = path.split("/")[-1]
        if webhook_id in mock_data.webhooks:
            self._send_json(mock_data.webhooks[webhook_id])
        else:
            self._send_not_found()

    def _handle_get_member(self, path):
        member_id = path.split("/")[-1]
        if member_id in mock_data.members:
            self._send_json(mock_data.members[member_id])
        else:
            self._send_not_found()

    def _handle_get_label(self, path):
        label_id = path.split("/")[-1]
        if label_id in mock_data.labels:
            self._send_json(mock_data.labels[label_id])
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
        parts = path.split("/")
        if path == "/1/boards":
            self._create_board(params, post_data)
        elif path == "/1/lists":
            self._create_list(params, post_data)
        elif path == "/1/cards":
            self._create_card(params, post_data)
        elif path == "/1/labels":
            self._create_label(params, post_data)
        elif path == "/1/checklists":
            self._create_checklist(params, post_data)
        elif path == "/1/webhooks":
            self._create_webhook(params, post_data)
        elif len(parts) == 5 and parts[1] == "1" and parts[2] == "checklists" and parts[4] == "checkItems":
            self._create_check_item(parts[3], params, post_data)
        elif len(parts) == 6 and parts[1] == "1" and parts[2] == "cards" and parts[4] == "actions" and parts[5] == "comments":
            self._create_comment(parts[3], params, post_data)
        elif len(parts) == 5 and parts[1] == "1" and parts[2] == "cards" and parts[4] == "attachments":
            self._create_attachment(parts[3], params, post_data)
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

    def _create_label(self, params, post_data):
        name = post_data.get('name') or params.get('name', [None])[0]
        color = post_data.get('color') or params.get('color', [None])[0]
        board_id = post_data.get('idBoard') or params.get('idBoard', [None])[0]
        if not name or not board_id:
            self._send_bad_request("name or idBoard")
            return
        new_id = str(uuid.uuid4())
        new_label = {
            "id": new_id,
            "name": name,
            "color": color,
            "idBoard": board_id,
        }
        mock_data.labels[new_id] = new_label
        self._send_json(new_label)

    def _create_checklist(self, params, post_data):
        name = post_data.get('name') or params.get('name', [None])[0]
        card_id = post_data.get('idCard') or params.get('idCard', [None])[0]
        if not name or not card_id:
            self._send_bad_request("name or idCard")
            return
        if card_id not in mock_data.cards:
            self._send_bad_request("idCard")
            return
        new_id = str(uuid.uuid4())
        new_checklist = {
            "id": new_id,
            "name": name,
            "idCard": card_id,
            "checkItems": [],
        }
        mock_data.checklists[new_id] = new_checklist
        self._send_json(new_checklist)

    def _create_check_item(self, checklist_id, params, post_data):
        if checklist_id not in mock_data.checklists:
            self._send_not_found()
            return
        name = post_data.get('name') or params.get('name', [None])[0]
        if not name:
            self._send_bad_request("name")
            return
        new_id = str(uuid.uuid4())
        new_check_item = {
            "id": new_id,
            "name": name,
            "state": "incomplete",
            "idChecklist": checklist_id,
        }
        mock_data.check_items[new_id] = new_check_item
        mock_data.checklists[checklist_id]["checkItems"].append(new_check_item)
        self._send_json(new_check_item)

    def _create_comment(self, card_id, params, post_data):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        text = post_data.get('text') or params.get('text', [None])[0]
        if not text:
            self._send_bad_request("text")
            return
        new_id = str(uuid.uuid4())
        new_comment = {
            "id": new_id,
            "text": text,
            "date": "2026-01-01T00:00:00.000Z",
            "idMemberCreator": "mock_member_id",
            "idCard": card_id,
        }
        mock_data.comments[new_id] = new_comment
        self._send_json(new_comment)

    def _create_attachment(self, card_id, params, post_data):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        url = post_data.get('url') or params.get('url', [None])[0]
        if not url:
            self._send_bad_request("url")
            return
        name = post_data.get('name') or params.get('name', [None])[0] or url
        new_id = str(uuid.uuid4())
        new_attachment = {
            "id": new_id,
            "name": name,
            "url": url,
            "bytes": 0,
            "date": "2026-01-01T00:00:00.000Z",
            "idMember": "mock_member_id",
            "idCard": card_id,
        }
        mock_data.attachments[new_id] = new_attachment
        self._send_json(new_attachment)

    def _create_webhook(self, params, post_data):
        callback_url = post_data.get('callbackURL') or params.get('callbackURL', [None])[0]
        id_model = post_data.get('idModel') or params.get('idModel', [None])[0]
        if not callback_url or not id_model:
            self._send_bad_request("callbackURL or idModel")
            return
        description = post_data.get('description') or params.get('description', [""])[0]
        new_id = str(uuid.uuid4())
        new_webhook = {
            "id": new_id,
            "description": description,
            "callbackURL": callback_url,
            "idModel": id_model,
            "active": True,
        }
        mock_data.webhooks[new_id] = new_webhook
        self._send_json(new_webhook)

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
        elif path.startswith("/1/labels/"):
            self._update_label(path, update_data)
        elif path.startswith("/1/actions/"):
            self._update_comment(path, update_data)
        elif path.startswith("/1/webhooks/"):
            self._update_webhook(path, update_data)
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
        elif len(parts) == 6 and parts[4] == "checkItem":
            self._update_check_item(parts[5], update_data)

    def _update_check_item(self, check_item_id, update_data):
        if check_item_id not in mock_data.check_items:
            self._send_not_found()
            return
        mock_data.check_items[check_item_id].update(update_data)
        self._send_json(mock_data.check_items[check_item_id])

    def _update_label(self, path, update_data):
        label_id = path.split("/")[-1]
        if label_id in mock_data.labels:
            mock_data.labels[label_id].update(update_data)
            self._send_json(mock_data.labels[label_id])
        else:
            self._send_not_found()

    def _update_comment(self, path, update_data):
        comment_id = path.split("/")[-1]
        if comment_id in mock_data.comments:
            mock_data.comments[comment_id].update(update_data)
            self._send_json(mock_data.comments[comment_id])
        else:
            self._send_not_found()

    def _update_webhook(self, path, update_data):
        webhook_id = path.split("/")[-1]
        if webhook_id in mock_data.webhooks:
            mock_data.webhooks[webhook_id].update(update_data)
            self._send_json(mock_data.webhooks[webhook_id])
        else:
            self._send_not_found()

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
        parts = path.split("/")
        if path.startswith("/1/boards/"):
            self._delete_board(path)
        elif path.startswith("/1/cards/") and len(parts) == 6 and parts[4] == "attachments":
            self._delete_attachment(parts[3], parts[5])
        elif path.startswith("/1/cards/"):
            self._delete_card(path)
        elif path.startswith("/1/labels/"):
            self._delete_label(path)
        elif path.startswith("/1/checklists/") and len(parts) == 6 and parts[4] == "checkItems":
            self._delete_check_item(parts[3], parts[5])
        elif path.startswith("/1/checklists/"):
            self._delete_checklist(path)
        elif path.startswith("/1/actions/"):
            self._delete_comment(path)
        elif path.startswith("/1/webhooks/"):
            self._delete_webhook(path)
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

    def _delete_label(self, path):
        label_id = path.split("/")[-1]
        if label_id in mock_data.labels:
            del mock_data.labels[label_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()

    def _delete_checklist(self, path):
        checklist_id = path.split("/")[-1]
        if checklist_id in mock_data.checklists:
            items_to_remove = [
                cid for cid, ci in mock_data.check_items.items()
                if ci["idChecklist"] == checklist_id
            ]
            for cid in items_to_remove:
                del mock_data.check_items[cid]
            del mock_data.checklists[checklist_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()

    def _delete_check_item(self, checklist_id, check_item_id):
        if checklist_id not in mock_data.checklists:
            self._send_not_found()
            return
        if check_item_id not in mock_data.check_items:
            self._send_not_found()
            return
        checklist = mock_data.checklists[checklist_id]
        checklist["checkItems"] = [
            ci for ci in checklist["checkItems"] if ci["id"] != check_item_id
        ]
        del mock_data.check_items[check_item_id]
        self._send_json({"_value": None})

    def _delete_comment(self, path):
        comment_id = path.split("/")[-1]
        if comment_id in mock_data.comments:
            del mock_data.comments[comment_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()

    def _delete_attachment(self, card_id, attachment_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        if attachment_id not in mock_data.attachments:
            self._send_not_found()
            return
        del mock_data.attachments[attachment_id]
        self._send_json({"_value": None})

    def _delete_webhook(self, path):
        webhook_id = path.split("/")[-1]
        if webhook_id in mock_data.webhooks:
            del mock_data.webhooks[webhook_id]
            self._send_json({"_value": None})
        else:
            self._send_not_found()
