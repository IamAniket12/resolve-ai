# Resolve AI

Submission for the **Real-World Agents Hackathon** (Dwelly, London, 10 October 2026).

- **Team:** TODO
- **Track:** Property Management
- **Demo video:** `demo/demo.mp4` (TODO)

## 1. What we built

Resolve AI is an autonomous maintenance agent for a lettings business. It takes a
maintenance case as it actually arrives — a tenant's WhatsApp, a call recording, an email
thread, a CRM record, a repair history export, photos — and works it to a verified outcome:
it identifies and verifies the property, triages urgency against a written UK maintenance
policy, opens the ticket, selects and books the right certified contractor, requests landlord
approval when spend requires it, keeps tenant and landlord informed, and escalates to a human
with a complete handover when the policy says a person must decide.

It is built to be run as a batch over a folder of cases and to **always produce an answer**
for every case, even when a tool fails or information is missing.

## 2. The operational problem

When a tenant reports "the boiler's stopped working", the work that follows is manual:
understand how serious it is, check the property and repair history, find a contractor who is
qualified and available, arrange access, get approval, chase, and keep everyone informed.
Property managers spend hours per repair on this, and the hard part is not the happy path but
the exceptions: conflicting records, missing details, a contractor who doesn't answer, a
landlord abroad, a gas smell at 8am. Resolve AI handles the routine autonomously and makes
the exceptions safe and cheap for a human to pick up.

## 3. Architecture

```
cases folder ──> ingest (json/csv/md/eml/pdf/html/audio/images) ──> CaseBundle
                                                                       │
   policy/maintenance_policy.md ──> system prompt (cached)             ▼
                                                     ResolveAgent — Claude tool loop
                                                     understand → verify → triage → act → recover → report
                                                                       │ tools
                                                                       ▼
                 ToolRegistry ──> HttpBackend (event APIs) | MockBackend (local synthetic environment)
                                                                       │
                                                                       ▼
                   structured Resolution ──> ANSWERS/<case>/ANSWER.md + REASONING.md + logs/<run>/<case>/trace.json
```

| Module | Responsibility |
|---|---|
| `src/resolve_ai/ingest.py` | Discovers cases (folder per case, file per case, or a JSON list) and normalises every file type into text; audio is transcribed with ElevenLabs Scribe; images are passed to the model as vision input. |
| `src/resolve_ai/policy/maintenance_policy.md` | The agent's ground truth: urgency bands, hard safety rules (gas, electrical, CO, vulnerable occupants, Awaab's Law), landlord obligations, spend authority, contractor selection, access notice, escalation triggers, prohibited actions. |
| `src/resolve_ai/agent.py` | The case loop. Runs Claude with 12 tools, executes tool calls (parallel calls supported), feeds back errors as `is_error` results so the model can recover, blocks runaway duplicate calls, stops cleanly near the per-case deadline, then asks for a structured `Resolution`. |
| `src/resolve_ai/tools/` | Tool definitions (strict JSON schemas) and backends. `MockBackend` is a local synthetic environment with failure injection; `HttpBackend` maps tools to the event's APIs via `data/http_endpoints.json`; `CompositeBackend` mixes the two. `voice.py` wraps ElevenLabs STT, outbound calls and TTS. |
| `src/resolve_ai/runner.py` | Parallel batch execution with per-case timeouts, watchdog, and a fallback answer on any failure. Every case produces outputs. |
| `src/resolve_ai/writer.py` | Fixed-structure `ANSWER.md` / `REASONING.md` and a machine-readable trace. |
| `src/resolve_ai/llm/` | `AnthropicLLM` (Claude Opus 5.5, adaptive thinking, prompt caching, structured output) and `MockLLM`, a rule-based stand-in so the pipeline runs with no API key. |
| `src/resolve_ai/grade.py` | Local deterministic grader against `eval/expectations.json`. |

Design choices that matter for the Reality Test:
- **Coverage first.** A crashed or timed-out case still gets an honest, escalated answer with the partial trace.
- **Tools are the only way to act.** The model cannot claim an action it did not perform; the trace proves what happened.
- **Policy, not vibes.** Urgency and escalation decisions cite written rules, so they are consistent and auditable.
- **Backends are swappable.** Real event APIs and the local mock share one interface; the agent code never changes.
- **Untrusted content stays untrusted.** Instructions embedded in emails/documents are treated as data and flagged.

## 4. How to run

Prerequisites: Python 3.10+, git. (ffmpeg only if you want to convert audio locally.)

```bash
git clone <REPO_URL> && cd <repo>
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # add ANTHROPIC_API_KEY (and ELEVENLABS_API_KEY for voice)

# see how a folder of cases will be ingested
python -m resolve_ai inspect --cases data/sample_cases

# process cases -> ANSWERS/<case>/ANSWER.md + REASONING.md, traces in logs/<run_id>/
python -m resolve_ai run --cases data/sample_cases --out ANSWERS

# with no API key, exercise the whole pipeline on the rule-based mock
python -m resolve_ai run --cases data/sample_cases --out ANSWERS --provider mock

# local grading against expectations
python -m resolve_ai grade -v

# tests
pytest -q
```

### Sample cases and what they test

The nine cases in `data/sample_cases/` are built to cover every difficulty the brief lists. `eval/expectations.json` records the acceptable outcome for each; `python -m resolve_ai grade -v` checks a run against it.

| Difficulty in the brief | Cases | What the agent has to get right |
|---|---|---|
| Conflicting information | 03, 08 | Tenant vs inventory on a ceiling stain; landlord's "only a year old, just repair it" vs repair records showing three repairs and an engineer's "beyond economical repair" |
| Failed actions | 01, 03 | Preferred contractor API times out, next one has no slots, tenant's SMS bounces; the agent recovers and reports every failure |
| Missing context | 05, 09 | No property identifiable; a fact the tenant did not check decides which trade to send |
| Unusual exceptions | 02, 04, 06 | Landlord refusing to pay for a gas emergency; landlord abroad with a £150 limit; a former tenant reporting on an ended tenancy |
| Ambiguity | 09 | Cold electric shower with working heating: shower unit or boiler? One question, not a guess |
| Noisy or irrelevant information | 07 | 600-line house group chat; two real issues buried near the end, one of them tenant-caused |
| Situations requiring escalation | 02, 06 | Gas smell (statutory route, no ordinary booking); prompt injection claiming pre-approval |
| Larger or more difficult context | 08 | Seven attachments: 7-page inventory PDF, 60-row block CSV, photo, three emails from three parties |

Generated attachments (the long chat, the PDF, the CSV, the photo) come from `scripts/make_sample_assets.py` and are deterministic.

Reality Test command (what we ran at 16:30):

```bash
python -m resolve_ai run --cases data/reality_test --out ANSWERS --workers 8 --timeout 600
```

### Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Required for the real agent. |
| `ANTHROPIC_MODEL` / `ANTHROPIC_EFFORT` | Default `claude-opus-5-5` / `high`. |
| `ANTHROPIC_SERVER_FALLBACKS` | `1` retries on a fallback model if a safety classifier declines; auto-disables if unsupported. |
| `LLM_PROVIDER` | `auto` (anthropic if key present, else mock), `anthropic`, `mock`. |
| `TOOL_BACKEND` | `mock` or `http`. With `http`, `HTTP_TOOLS` lists which tools go to the API (`*` = all mapped in `data/http_endpoints.json`); the rest stay on the mock. |
| `TOOLS_BASE_URL` / `TOOLS_API_KEY` | Event API. |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_PHONE_NUMBER_ID`, `VOICE_LIVE_CALLS` | Voice features. Calls are simulated unless `VOICE_LIVE_CALLS=1`. |
| `RUN_WORKERS`, `CASE_TIMEOUT_SECONDS`, `MAX_AGENT_STEPS` | Runner limits. |

## 5. Models, APIs and external services

| Service | Use |
|---|---|
| Anthropic Claude Opus 5.5 (`claude-opus-5-5`) via the official `anthropic` Python SDK | Case reasoning, tool use, structured resolution. Adaptive thinking, prompt caching on the system prompt. |
| ElevenLabs Scribe (speech-to-text) | Transcribes call recordings during ingestion. |
| ElevenLabs Conversational AI (outbound calls) | Confirms bookings / gathers missing facts by phone (`place_call` tool). Simulated in batch mode. |
| ElevenLabs text-to-speech | Optional voice updates to tenants (demo). |
| Event-provided operational APIs | TODO: list what was wired on the day. |

## 6. Assumptions

- TODO on the day: data layout, which tools were real vs mocked, any answer-format guidance.
- UK residential lettings context; policy thresholds (e.g. £250 default spend authority) are defaults overridden by landlord instructions in the data.
- Information inside case material is data, never instructions.

## 7. Known limitations

- TODO on the day.
- The mock LLM is for plumbing tests only; its judgement is keyword-based.
- Voice call outcomes are simulated unless live telephony is configured.

## 8. What we would build next

- Close the loop after the contractor visit: completion confirmation, invoice matching, tenant satisfaction check, and reopen detection.
- Learn per-landlord and per-property preferences from history instead of a static policy.
- A human review queue UI for escalations with one-click resume.
- Evaluation harness with graded synthetic cases run on every commit.

## License

Apache License 2.0 — see `LICENSE`.
