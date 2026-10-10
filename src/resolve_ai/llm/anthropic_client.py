"""Claude via the official Anthropic SDK (manual tool loop driven by agent.py)."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import anthropic

from resolve_ai.config import Settings
from resolve_ai.llm import LLM, LLMResponse

log = logging.getLogger(__name__)

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicLLM(LLM):
    name = "anthropic"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.model
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key or None,
                                          timeout=settings.request_timeout, max_retries=3)
        self.use_fallbacks = settings.server_fallbacks

    # ---- low level ----
    def _create(self, **kw):
        if self.use_fallbacks:
            try:
                return self.client.beta.messages.create(betas=[FALLBACK_BETA], fallbacks="default", **kw)
            except anthropic.BadRequestError as e:
                # Fallback parameter unsupported in this environment -> degrade once, keep going.
                log.warning("server-side fallbacks rejected (%s); continuing without them", e.message)
                self.use_fallbacks = False
        return self.client.messages.create(**kw)

    @staticmethod
    def _with_cache_breakpoints(messages: List[dict]) -> List[dict]:
        """Copy the messages and mark two cache breakpoints: the case material (first user message) and the
        latest turn. With the system prompt that is three of the four allowed. Every step then re-reads the whole
        prefix from cache instead of paying full price for it. Markers never accumulate because we copy each time."""
        import copy
        msgs = copy.deepcopy(messages)
        if not msgs:
            return msgs

        def blocks(m: dict) -> List[dict]:
            if isinstance(m["content"], str):
                m["content"] = [{"type": "text", "text": m["content"]}]
            return m["content"]

        def mark(m: dict) -> None:
            bl = blocks(m)
            for b in reversed(bl):
                if isinstance(b, dict) and b.get("type") in {"text", "tool_result", "image", "document"}:
                    b["cache_control"] = {"type": "ephemeral"}
                    return

        mark(msgs[0])
        if len(msgs) > 1:
            mark(msgs[-1])
        return msgs

    def _common(self, system: str, messages: List[dict], tools: List[dict]) -> Dict[str, Any]:
        return {
            "model": self.model,
            "max_tokens": 16000,
            "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            "messages": self._with_cache_breakpoints(messages),
            "tools": tools,
            "thinking": {"type": "adaptive"},
        }

    @staticmethod
    def _dump(resp) -> List[Dict[str, Any]]:
        return [b.model_dump(exclude_none=True) for b in resp.content]

    @staticmethod
    def _usage(resp) -> Dict[str, int]:
        u = resp.usage
        return {
            "input_tokens": getattr(u, "input_tokens", 0) or 0,
            "output_tokens": getattr(u, "output_tokens", 0) or 0,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
        }

    # ---- API ----
    def step(self, system: str, messages: List[dict], tools: List[dict]) -> LLMResponse:
        kw = self._common(system, messages, tools)
        kw["output_config"] = {"effort": self.settings.effort}
        resp = self._create(**kw)
        if resp.stop_reason == "refusal":
            details = getattr(resp, "stop_details", None)
            log.warning("model refusal: %s", details)
        return LLMResponse(self._dump(resp), resp.stop_reason or "end_turn", self._usage(resp), resp.model)

    def finalize(self, system: str, messages: List[dict], tools: List[dict], schema: dict) -> Dict[str, Any]:
        kw = self._common(system, messages, tools)
        kw["tool_choice"] = {"type": "none"}
        kw["output_config"] = {"effort": self.settings.effort, "format": {"type": "json_schema", "schema": schema}}
        resp = self._create(**kw)
        text = next((b.text for b in resp.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"finalize returned non-JSON ({e}): {text[:300]}") from e
        data["_usage"] = self._usage(resp)
        return data
