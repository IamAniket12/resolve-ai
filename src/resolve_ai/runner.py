"""Batch runner: every case gets an answer, no matter what.

- cases run in parallel threads
- each case has a hard deadline; the agent stops early near it and a watchdog writes a
  fallback answer if it overruns
- any exception -> fallback answer (escalated, with partial trace)
- per-case trace.json + a run.log in logs/<run_id>/
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from resolve_ai.agent import ResolveAgent, fallback_result
from resolve_ai.config import Settings, load_policy
from resolve_ai.ingest import discover_cases
from resolve_ai.llm import make_llm
from resolve_ai.models import CaseBundle, CaseResult
from resolve_ai.tools.registry import ToolRegistry, build_backend
from resolve_ai.tools.voice import make_transcriber
from resolve_ai.writer import write_case, write_index

log = logging.getLogger("resolve")


def _setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh = logging.FileHandler(log_dir / "run.log", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    root.handlers = [fh, sh]
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


class CaseRun:
    """Holds partial state so a timeout can still produce a useful fallback."""

    def __init__(self, bundle: CaseBundle):
        self.bundle = bundle
        self.events = []
        self.result: Optional[CaseResult] = None


def run_cases(cases_path: str, answers_dir: str, settings: Settings, workers: Optional[int] = None,
              case_timeout: Optional[int] = None, only: Optional[List[str]] = None, run_id: Optional[str] = None) -> List[CaseResult]:
    run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = Path("logs") / run_id
    _setup_logging(log_dir)
    answers = Path(answers_dir)
    answers.mkdir(parents=True, exist_ok=True)
    workers = workers or settings.workers
    case_timeout = case_timeout or settings.case_timeout

    llm = make_llm(settings)
    policy = load_policy()
    agent = ResolveAgent(llm, settings, policy, registry_factory=lambda cid: ToolRegistry(build_backend(settings, cid)))

    bundles = discover_cases(cases_path, transcriber=make_transcriber(settings))
    if only:
        bundles = [b for b in bundles if b.case_id in set(only)]
    log.info("run %s: %d cases from %s | provider=%s model=%s tools=%s workers=%d timeout=%ds",
             run_id, len(bundles), cases_path, llm.name, llm.model, settings.tool_backend, workers, case_timeout)
    (log_dir / "run_meta.json").write_text(json.dumps({
        "run_id": run_id, "cases_path": cases_path, "n_cases": len(bundles), "provider": llm.name, "model": llm.model,
        "tool_backend": settings.tool_backend, "workers": workers, "case_timeout": case_timeout,
        "effort": settings.effort, "cases": [b.case_id for b in bundles]}, indent=2))

    results: List[CaseResult] = []
    lock = threading.Lock()

    def work(bundle: CaseBundle) -> CaseResult:
        deadline = time.time() + case_timeout
        t0 = time.time()
        try:
            r = agent.run(bundle, deadline=deadline, trace_cb=log.info, grace=min(60.0, case_timeout * 0.15))
        except Exception as e:  # noqa: BLE001
            log.exception("[%s] agent failed", bundle.case_id)
            r = fallback_result(bundle, f"{type(e).__name__}: {e}", provider=llm.name)
        log.info("[%s] %s in %.0fs -> %s / %s", bundle.case_id, r.status, time.time() - t0, r.resolution.decision, r.resolution.urgency)
        return r

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(work, b): b for b in bundles}
        for fut, bundle in futures.items():
            try:
                r = fut.result(timeout=case_timeout + 90)
            except cf.TimeoutError:
                log.error("[%s] hard timeout; writing fallback", bundle.case_id)
                r = fallback_result(bundle, f"timed out after {case_timeout}s", provider=llm.name)
            except Exception as e:  # noqa: BLE001
                log.exception("[%s] unexpected failure", bundle.case_id)
                r = fallback_result(bundle, f"{type(e).__name__}: {e}", provider=llm.name)
            try:
                write_case(r, answers, log_dir)
            except Exception as e:  # noqa: BLE001
                log.exception("[%s] could not write outputs: %s", bundle.case_id, e)
                r = fallback_result(bundle, f"writer failure: {e}", provider=llm.name)
                write_case(r, answers, log_dir)
            with lock:
                results.append(r)

    write_index(results, answers)
    done = sum(1 for r in results if r.status == "completed")
    log.info("run %s finished: %d/%d completed, %d fallback. Answers in %s, logs in %s",
             run_id, done, len(results), len(results) - done, answers, log_dir)
    return results
