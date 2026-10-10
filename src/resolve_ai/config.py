"""Runtime settings, all from environment variables (see .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PACKAGE_DIR = Path(__file__).resolve().parent
POLICY_PATH = PACKAGE_DIR / "policy" / "maintenance_policy.md"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _flag(name: str, default: str = "0") -> bool:
    return _env(name, default).lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    # model
    anthropic_api_key: str = _env("ANTHROPIC_API_KEY")
    model: str = _env("ANTHROPIC_MODEL", "claude-opus-5-5")
    effort: str = _env("ANTHROPIC_EFFORT", "high")
    fallback_model: str = _env("ANTHROPIC_FALLBACK_MODEL", "claude-sonnet-5-5")  # used once per case if the primary model keeps failing
    server_fallbacks: bool = _flag("ANTHROPIC_SERVER_FALLBACKS", "1")
    request_timeout: float = float(_env("ANTHROPIC_REQUEST_TIMEOUT", "240"))
    llm_provider: str = _env("LLM_PROVIDER", "auto")  # auto | anthropic | mock

    # tools
    tool_backend: str = _env("TOOL_BACKEND", "mock")  # mock | http
    tools_base_url: str = _env("TOOLS_BASE_URL")
    tools_api_key: str = _env("TOOLS_API_KEY")
    mock_env_dir: str = _env("MOCK_ENV_DIR", "data/mock_env")
    # comma-separated tool names routed to the HTTP backend when TOOL_BACKEND=http; "*" = all mapped
    http_tools: set = None  # type: ignore[assignment]

    # voice
    elevenlabs_api_key: str = _env("ELEVENLABS_API_KEY")
    elevenlabs_agent_id: str = _env("ELEVENLABS_AGENT_ID")
    elevenlabs_phone_number_id: str = _env("ELEVENLABS_PHONE_NUMBER_ID")
    voice_live_calls: bool = _flag("VOICE_LIVE_CALLS", "0")

    # runner
    workers: int = int(_env("RUN_WORKERS", "6"))
    case_timeout: int = int(_env("CASE_TIMEOUT_SECONDS", "600"))
    max_steps: int = int(_env("MAX_AGENT_STEPS", "30"))

    def __post_init__(self):
        raw = _env("HTTP_TOOLS", "*")
        self.http_tools = {t.strip() for t in raw.split(",") if t.strip()}

    def resolved_provider(self) -> str:
        if self.llm_provider == "auto":
            return "anthropic" if self.anthropic_api_key else "mock"
        return self.llm_provider


def load_policy() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")
