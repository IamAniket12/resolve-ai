"""Proves the 'supplied tools' path: tools mapped in an endpoints file are called over HTTP with the
right method, path placeholders, query/body, auth headers and error handling. Uses a local stdlib server."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from resolve_ai.config import Settings
from resolve_ai.tools import http_backend
from resolve_ai.tools.registry import ToolError, ToolRegistry, build_backend

SEEN = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silence
        pass

    def _reply(self, code: int, body: dict):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        SEEN.append(("GET", self.path, dict(self.headers), None))
        if self.path.startswith("/properties/search"):
            return self._reply(200, {"found": True, "property_id": "EV-1", "address": "1 Event Street"})
        if self.path.startswith("/contractors/CON-X/availability"):
            return self._reply(504, {"error": "upstream timeout"})
        return self._reply(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        SEEN.append(("POST", self.path, dict(self.headers), body))
        if self.path == "/tickets":
            return self._reply(201, {"ticket_id": "EV-TKT-1", **body})
        if self.path.startswith("/tickets/") and self.path.endswith("/notes"):
            return self._reply(200, {"note_id": "EV-NOTE-1"})
        return self._reply(404, {"error": "not found"})


@pytest.fixture(scope="module")
def server():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture
def endpoints(tmp_path, monkeypatch):
    f = tmp_path / "endpoints.json"
    f.write_text(json.dumps({
        "lookup_property": {"method": "GET", "path": "/properties/search"},
        "check_contractor_availability": {"method": "GET", "path": "/contractors/{contractor_id}/availability"},
        "create_maintenance_ticket": {"method": "POST", "path": "/tickets"},
        "record_note": {"method": "POST", "path": "/tickets/{ticket_id}/notes"},
    }))
    monkeypatch.setattr(http_backend, "ENDPOINTS_FILE", Path(f))
    return f


def _settings(base: str) -> Settings:
    s = Settings()
    s.tool_backend = "http"
    s.tools_base_url = base
    s.tools_api_key = "test-token"
    s.http_tools = {"*"}
    return s


def test_http_tools_are_called_with_auth_placeholders_and_bodies(server, endpoints):
    SEEN.clear()
    reg = ToolRegistry(build_backend(_settings(server), "t1"))
    r = reg.call("lookup_property", {"query": "1 Event Street"})
    assert r["found"] and r["property_id"] == "EV-1"
    method, path, headers, _ = SEEN[-1]
    assert method == "GET" and path == "/properties/search?query=1+Event+Street"
    assert headers.get("Authorization") == "Bearer test-token" and headers.get("x-api-key") == "test-token"

    t = reg.call("create_maintenance_ticket", {"property_id": "EV-1", "title": "Leak", "category": "plumbing",
                                               "urgency": "urgent", "description": "d", "reported_by": "tenant"})
    assert t["ticket_id"] == "EV-TKT-1"
    assert SEEN[-1][0] == "POST" and SEEN[-1][3]["title"] == "Leak"

    n = reg.call("record_note", {"ticket_id": "EV-TKT-1", "note": "hello"})
    assert n["note_id"] == "EV-NOTE-1"
    assert SEEN[-1][1] == "/tickets/EV-TKT-1/notes" and SEEN[-1][3] == {"note": "hello"}  # placeholder removed from body


def test_http_errors_become_tool_errors_and_unmapped_tools_fall_back_to_mock(server, endpoints):
    reg = ToolRegistry(build_backend(_settings(server), "t2"))
    with pytest.raises(ToolError) as e:
        reg.call("check_contractor_availability", {"contractor_id": "CON-X", "urgency": "urgent"})
    assert "HTTP 504" in str(e.value)
    # search_contractors has no HTTP mapping -> served by the mock, so the agent is never stranded
    r = reg.call("search_contractors", {"trade": "plumber", "postcode": "SE15 4QJ", "emergency": False})
    assert r["contractors"]


def test_composite_routes_only_listed_tools(server, endpoints):
    s = _settings(server)
    s.http_tools = {"lookup_property"}
    reg = ToolRegistry(build_backend(s, "t3"))
    SEEN.clear()
    reg.call("lookup_property", {"query": "x"})
    assert SEEN and SEEN[-1][1].startswith("/properties/search")
    before = len(SEEN)
    reg.call("create_maintenance_ticket", {"property_id": "PROP-0042", "title": "t", "category": "c", "urgency": "routine",
                                           "description": "d", "reported_by": "tenant"})
    assert len(SEEN) == before  # went to the mock, not HTTP
