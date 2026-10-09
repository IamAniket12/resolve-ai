"""LLM backends. Both return plain-dict content blocks in the Anthropic Messages shape
so the agent loop is identical whichever backend is in use."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from resolve_ai.config import Settings


@dataclass
class LLMResponse:
    content: List[Dict[str, Any]]
    stop_reason: str
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""


class LLM:
    name = "base"
    model = ""

    def step(self, system: str, messages: List[dict], tools: List[dict]) -> LLMResponse:
        raise NotImplementedError

    def finalize(self, system: str, messages: List[dict], tools: List[dict], schema: dict) -> Dict[str, Any]:
        raise NotImplementedError


def make_llm(settings: Settings) -> LLM:
    provider = settings.resolved_provider()
    if provider == "anthropic":
        from resolve_ai.llm.anthropic_client import AnthropicLLM
        return AnthropicLLM(settings)
    if provider == "mock":
        from resolve_ai.llm.mock_llm import MockLLM
        return MockLLM(settings)
    raise ValueError(f"unknown LLM_PROVIDER {provider}")
