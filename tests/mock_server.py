import http.server
import socketserver
import json
import time
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
        self.attachment_content = {}
        self.webhooks = {}
        self.forced_error = None
        self.forced_delay = None

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

    def _send_json(self, data, status=200, extra_headers=None):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
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
        return urllib.parse.parse_qs(parsed_path.query, keep_blank_values=True)

    def _is_authenticated(self, query_params):
        key = query_params.get('key', [None])[0]
        token = query_params.get('token', [None])[0]
        return key == "valid_api_key" and token == "valid_api_token"

    def _apply_forced_delay(self):
        if mock_data.forced_delay:
            time.sleep(mock_data.forced_delay)

    def _has_forced_error(self):
        if mock_data.forced_error:
            extra_headers = mock_data.forced_error.get("headers")
            self._send_json(mock_data.forced_error["body"], status=mock_data.forced_error["status"], extra_headers=extra_headers)
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

    def _handle_mock_file_download(self, path):
        attachment_id = path.split("/")[-1]
        if attachment_id in mock_data.attachment_content:
            content = mock_data.attachment_content[attachment_id]
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_not_found()

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        content_type = self.headers.get('Content-Type', '')
        if content_type.startswith('multipart/form-data'):
            return self._read_multipart(content_length, content_type)
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}

    def _read_multipart(self, content_length, content_type):
        body = self.rfile.read(content_length)
        boundary = None
        for part in content_type.split(';'):
            part = part.strip()
            if part.startswith('boundary='):
                boundary = part[len('boundary='):]
                break
        if not boundary:
            return {}

        fields = {}
        files = {}
        parts = body.split(f'--{boundary}'.encode())
        for part in parts:
            if not part or part.strip() in (b'', b'--', b'--\r\n'):
                continue
            if b'\r\n\r\n' not in part:
                continue
            header_section, body_section = part.split(b'\r\n\r\n', 1)
            if body_section.endswith(b'\r\n'):
                body_section = body_section[:-2]
            headers_text = header_section.decode('utf-8', errors='replace')
            name = None
            filename = None
            for line in headers_text.split('\r\n'):
                if 'Content-Disposition' in line:
                    for param in line.split(';'):
                        param = param.strip()
                        if param.startswith('name='):
                            name = param[5:].strip('"')
                        elif param.startswith('filename='):
                            filename = param[9:].strip('"')
            if filename:
                files[name] = {"filename": filename, "bytes": len(body_section), "content": body_section}
            elif name:
                fields[name] = body_section.decode('utf-8', errors='replace')
        fields['_files'] = files
        return fields

    # --- GET ---

    def do_GET(self):
        self._apply_forced_delay()
        if self._has_forced_error():
            return
        path = self._parse_path()
        # Mock file download route (no auth — simulates CDN URL)
        if path.startswith("/mock-files/"):
            self._handle_mock_file_download(path)
            return
        params = self._get_query_params()
        if not self._is_authenticated(params):
            self._send_invalid_key()
            return
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
        elif path == "/1/search":
            self._handle_search(params or {})
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
        elif len(parts) == 6 and parts[4] == "attachments":
            self._handle_get_single_attachment(card_id, parts[5])
        elif len(parts) == 5 and parts[4] == "checklists":
            self._handle_get_card_checklists(card_id)
        else:
            self._send_not_found()

    def _handle_get_card_checklists(self, card_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        card_checklists = []
        for cl in mock_data.checklists.values():
            if cl["idCard"] == card_id:
                checklist = dict(cl)
                checklist["checkItems"] = [
                    ci for ci in mock_data.check_items.values()
                    if ci["idChecklist"] == cl["id"]
                ]
                card_checklists.append(checklist)
        self._send_json(card_checklists)

    def _handle_get_card_comments(self, card_id, params):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        filter_value = params.get('filter', [None])[0]
        if filter_value == "commentCard":
            card_comments = [c for c in mock_data.comments.values() if c["data"]["card"]["id"] == card_id]
            self._send_json(card_comments)
        else:
            self._send_json([])

    def _handle_get_card_attachments(self, card_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        card_attachments = [a for a in mock_data.attachments.values() if a["idCard"] == card_id]
        self._send_json(card_attachments)

    def _handle_get_single_attachment(self, card_id, attachment_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        if attachment_id not in mock_data.attachments:
            self._send_not_found()
            return
        att = mock_data.attachments[attachment_id]
        if att["idCard"] != card_id:
            self._send_not_found()
            return
        self._send_json(att)

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

    def _handle_search(self, params):
        query = params.get('query', [None])[0]
        if not query:
            self._send_bad_request("query")
            return
        boards_limit = int(params.get('boards_limit', [10])[0])
        cards_limit = int(params.get('cards_limit', [10])[0])
        query_lower = query.lower()
        matching_boards = [
            b for b in mock_data.boards.values()
            if query_lower in b["name"].lower() or query_lower in b.get("desc", "").lower()
        ][:boards_limit]
        matching_cards = [
            c for c in mock_data.cards.values()
            if query_lower in c["name"].lower() or query_lower in c.get("desc", "").lower()
        ][:cards_limit]
        self._send_json({"boards": matching_boards, "cards": matching_cards})

    def _handle_get_label(self, path):
        label_id = path.split("/")[-1]
        if label_id in mock_data.labels:
            self._send_json(mock_data.labels[label_id])
        else:
            self._send_not_found()

    # --- POST ---

    def do_POST(self):
        self._apply_forced_delay()
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
        elif len(parts) == 5 and parts[1] == "1" and parts[2] == "cards" and parts[4] == "idLabels":
            self._add_label_to_card(parts[3], params, post_data)
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
        card = mock_data.cards[card_id]
        new_comment = {
            "id": new_id,
            "idMemberCreator": "mock_member_id",
            "type": "commentCard",
            "date": "2026-01-01T00:00:00.000Z",
            "data": {
                "text": text,
                "card": {"id": card_id, "name": card["name"]},
                "board": {"id": card.get("idBoard", "mock_board_id")},
            },
            "memberCreator": {
                "id": "mock_member_id",
                "username": "mock_user",
            },
        }
        mock_data.comments[new_id] = new_comment
        self._send_json(new_comment)

    def _add_label_to_card(self, card_id, params, post_data):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        # Trello API requires 'value' in POST body, not query params
        label_id = post_data.get('value')
        if not label_id:
            self._send_bad_request("value")
            return
        if label_id not in mock_data.labels:
            self._send_not_found()
            return
        card = mock_data.cards[card_id]
        if label_id not in card["idLabels"]:
            card["idLabels"].append(label_id)
            card["labels"].append(mock_data.labels[label_id])
        self._send_json(card["idLabels"])

    def _create_attachment(self, card_id, params, post_data):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        files = post_data.get('_files', {})
        new_id = str(uuid.uuid4())
        if 'file' in files:
            file_info = files['file']
            name = params.get('name', [None])[0] or post_data.get('name') or file_info['filename']
            url = f"http://127.0.0.1:{PORT}/mock-files/{new_id}"
            file_bytes = file_info['bytes']
            mock_data.attachment_content[new_id] = file_info.get("content", b"")
        else:
            url = post_data.get('url') or params.get('url', [None])[0]
            if not url:
                self._send_bad_request("url")
                return
            name = post_data.get('name') or params.get('name', [None])[0] or url
            file_bytes = 0
        new_attachment = {
            "id": new_id,
            "name": name,
            "url": url,
            "bytes": file_bytes,
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
        self._apply_forced_delay()
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
            if "idLabels" in update_data:
                raw = update_data.pop("idLabels")
                label_ids = [l.strip() for l in raw.split(",") if l.strip()] if raw else []
                mock_data.cards[card_id]["idLabels"] = label_ids
                mock_data.cards[card_id]["labels"] = [
                    mock_data.labels[lid] for lid in label_ids if lid in mock_data.labels
                ]
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
            if "text" in update_data:
                mock_data.comments[comment_id]["data"]["text"] = update_data["text"]
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
        self._apply_forced_delay()
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
        elif path.startswith("/1/cards/") and len(parts) == 6 and parts[4] == "idLabels":
            self._remove_label_from_card(parts[3], parts[5])
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

    def _remove_label_from_card(self, card_id, label_id):
        if card_id not in mock_data.cards:
            self._send_not_found()
            return
        card = mock_data.cards[card_id]
        if label_id not in card["idLabels"]:
            self._send_not_found()
            return
        card["idLabels"].remove(label_id)
        card["labels"] = [l for l in card["labels"] if l["id"] != label_id]
        self._send_json({"_value": None})

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
