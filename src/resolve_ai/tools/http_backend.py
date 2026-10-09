"""Adapter for the hackathon's real APIs. We do not know the endpoints until 10:00 on
the day, so this is deliberately generic: every tool maps to an HTTP request described in
`data/http_endpoints.json`:

{
  "lookup_property": {"method": "GET", "path": "/properties/{query}"},
  "create_maintenance_ticket": {"method": "POST", "path": "/tickets"}
}

Path placeholders are filled from the tool payload; remaining fields go in the query
string (GET) or JSON body (others). Override `transform_<tool>` methods here if an
endpoint needs reshaping. Tools without a mapping fall back to the mock when used via
CompositeBackend.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from resolve_ai.config import Settings
from resolve_ai.tools.registry import ToolError

log = logging.getLogger(__name__)

ENDPOINTS_FILE = Path(os.environ.get("HTTP_ENDPOINTS_FILE", "data/http_endpoints.json"))


class HttpBackend:
    def __init__(self, settings: Settings):
        self.base = settings.tools_base_url.rstrip("/")
        self.session = requests.Session()
        if settings.tools_api_key:
            self.session.headers["Authorization"] = f"Bearer {settings.tools_api_key}"
            self.session.headers["x-api-key"] = settings.tools_api_key
        self.endpoints: Dict[str, Dict[str, Any]] = {}
        if ENDPOINTS_FILE.exists():
            self.endpoints = json.loads(ENDPOINTS_FILE.read_text())

    def has(self, tool: str) -> bool:
        return bool(self.base) and tool in self.endpoints

    def __getattr__(self, tool: str):
        if tool.startswith("_"):
            raise AttributeError(tool)

        def handler(**payload):
            return self._call(tool, payload)
        return handler

    def _call(self, tool: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.base:
            raise ToolError("TOOLS_BASE_URL not configured")
        spec = self.endpoints.get(tool)
        if not spec:
            raise ToolError(f"no HTTP endpoint mapped for {tool}")
        transform = getattr(self, f"transform_{tool}", None)
        if transform:
            payload = transform(payload)
        path = spec["path"]
        remaining = dict(payload)
        for key in list(remaining):
            token = "{" + key + "}"
            if token in path:
                path = path.replace(token, str(remaining.pop(key)))
        method = spec.get("method", "POST").upper()
        url = self.base + path
        try:
            if method == "GET":
                r = self.session.get(url, params=remaining, timeout=30)
            else:
                r = self.session.request(method, url, json=remaining, timeout=30)
        except requests.RequestException as e:
            raise ToolError(f"{tool}: network error calling {url}: {e}") from e
        if r.status_code >= 400:
            raise ToolError(f"{tool}: HTTP {r.status_code} from {url}: {r.text[:500]}")
        try:
            return r.json() if r.content else {"status": "ok"}
        except ValueError:
            return {"status": "ok", "raw": r.text[:2000]}


class CompositeBackend:
    """Route some tools to HTTP, the rest to mock. http_tools: set of names or {'*'}."""

    def __init__(self, http: HttpBackend, mock, http_tools: Optional[set] = None):
        self.http = http
        self.mock = mock
        self.http_tools = http_tools or set()

    def _use_http(self, tool: str) -> bool:
        if "*" in self.http_tools:
            return self.http.has(tool)
        return tool in self.http_tools and self.http.has(tool)

    def __getattr__(self, tool: str):
        if tool.startswith("_"):
            raise AttributeError(tool)
        target = self.http if self._use_http(tool) else self.mock
        return getattr(target, tool)

    def snapshot(self):
        return self.mock.snapshot()
