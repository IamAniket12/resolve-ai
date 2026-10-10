"""Smoke tests: the pipeline must always produce an answer for every case."""
import json
from pathlib import Path

import pytest

from resolve_ai.agent import ResolveAgent, fallback_result
from resolve_ai.config import Settings, load_policy
from resolve_ai.ingest import discover_cases
from resolve_ai.llm.mock_llm import MockLLM
from resolve_ai.models import Resolution, resolution_schema
from resolve_ai.tools.registry import ToolRegistry, build_backend
from resolve_ai.writer import write_case

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "data" / "sample_cases"


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.chdir(ROOT)
    s = Settings()
    s.llm_provider = "mock"
    s.tool_backend = "mock"
    return s


def test_discover_sample_cases():
    bundles = discover_cases(SAMPLES)
    assert len(bundles) == 9
    assert all(b.attachments for b in bundles)
    kinds = {a.kind for b in bundles for a in b.attachments}
    assert {"json", "text", "email", "transcript", "pdf", "csv", "image"} <= kinds


def test_schema_is_strict():
    s = resolution_schema()
    assert s["additionalProperties"] is False
    assert set(s["required"]) == set(s["properties"])
    for d in s.get("$defs", {}).values():
        assert set(d["required"]) == set(d["properties"])


def test_every_case_gets_an_answer(settings, tmp_path):
    agent = ResolveAgent(MockLLM(settings), settings, load_policy(), lambda b: ToolRegistry(build_backend(settings, b.case_id, bundle=b)))
    for b in discover_cases(SAMPLES):
        r = agent.run(b)
        assert isinstance(r.resolution, Resolution)
        write_case(r, tmp_path / "ANSWERS", tmp_path / "logs")
        assert (tmp_path / "ANSWERS" / b.case_id / "ANSWER.md").exists()
        assert (tmp_path / "ANSWERS" / b.case_id / "REASONING.md").exists()
        trace = json.loads((tmp_path / "logs" / b.case_id / "trace.json").read_text())
        assert trace["status"] == "completed"


def test_gas_case_never_books(settings):
    agent = ResolveAgent(MockLLM(settings), settings, load_policy(), lambda b: ToolRegistry(build_backend(settings, b.case_id, bundle=b)))
    b = next(b for b in discover_cases(SAMPLES) if b.case_id == "02_gas_smell")
    r = agent.run(b)
    names = {e.name for e in r.tool_events}
    assert "schedule_contractor" not in names
    assert r.resolution.escalation.required
    assert "0800 111 999" in r.resolution.tenant_communication


def test_fallback_answer_is_complete(settings, tmp_path):
    b = discover_cases(SAMPLES)[0]
    r = fallback_result(b, "simulated crash")
    assert r.status == "fallback"
    assert r.resolution.decision == "escalated"
    write_case(r, tmp_path / "ANSWERS", tmp_path / "logs")
    text = (tmp_path / "ANSWERS" / b.case_id / "ANSWER.md").read_text()
    assert "simulated crash" in text


def test_anthropic_cache_breakpoints_do_not_accumulate():
    """The client marks the case material and the latest turn, never more, and never mutates the caller's messages."""
    from resolve_ai.llm.anthropic_client import AnthropicLLM
    from resolve_ai.config import Settings
    llm = AnthropicLLM(Settings())  # constructs without a key
    messages = [
        {"role": "user", "content": [{"type": "text", "text": "case material"}]},
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "x", "input": {}}]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "r1"}]},
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t2", "name": "x", "input": {}}]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t2", "content": "r2"}]},
    ]
    kw = llm._common("sys", messages, [])
    marked = [(i, b["type"]) for i, m in enumerate(kw["messages"]) for b in m["content"] if isinstance(b, dict) and "cache_control" in b]
    assert marked == [(0, "text"), (4, "tool_result")]
    assert all("cache_control" not in b for m in messages for b in m["content"])  # caller's copy untouched
    kw2 = llm._common("sys", messages + [{"role": "user", "content": "finalize"}], [])
    marked2 = [i for i, m in enumerate(kw2["messages"]) for b in m["content"] if isinstance(b, dict) and "cache_control" in b]
    assert marked2 == [0, 5]
