# Resolve AI — Hackathon Plan

Event: Dwelly Real-World Agents Hackathon, Saturday 10 October 2026, London.
Track: Property Management. Team: 3 people.

## What wins (read this first)

1. **The Reality Test is a batch job.** At 16:30 we get unseen cases and 30 minutes.
   One command must process every case in parallel and write `ANSWERS/<n>/ANSWER.md`
   and `REASONING.md` for each. A crashed case scores zero. A case that says
   "escalated because X failed, here is the handover" still scores on coverage + safety.
2. **The judge is Claude.** Automated judging agents read ANSWER.md / REASONING.md
   against required outcomes, acceptable alternatives, red flags, prohibited actions.
   Every answer uses the same explicit structure. Never address the judge.
3. **Dwelly cares about escalations.** Their Sept 2026 blog: ~5 human escalations per
   maintenance task today; they want fewer, safer ones with full context.
   Our pitch: *fewer, better escalations*.
4. **Rules conflict on the demo video.** Rules doc: code + video freeze at 16:30.
   Event page: record after 17:00. Plan for the stricter: video recorded by 16:15.
5. **Pre-built code is allowed.** This repo is the skeleton we walk in with.

## Scoring math (what to optimise)

| Component | Weight | What it really means |
|---|---|---|
| Correct outcomes | 35% of technical | Right decision per case, respects constraints |
| Coverage | 20% of technical | Every case produces an answer |
| Judgement & safety | 20% of technical | Conflicts, gaps, escalation, knowing when not to act |
| Engineering | 15% of technical | Autonomous, robust, reproducible, no manual steps |
| Real-world applicability | 10% of technical | Could Dwelly run this |
| Demo video | 30% overall | Working product, clear workflow, clear outcome |

## Architecture

```
cases folder ──> ingest (json/csv/md/eml/pdf/audio/images) ──> CaseBundle
                                                                  │
   policy/maintenance_policy.md ──> system prompt                 ▼
                                                        ResolveAgent (Claude Opus 5.5 tool loop)
                                                                  │  tools via ToolRegistry
                                                                  ▼
                       ToolBackend: HttpBackend (event APIs) | MockBackend (local JSON state)
                                                                  │
                                                                  ▼
                          structured Resolution ──> ANSWER.md + REASONING.md + logs/trace
```

Layers:
- `ingest.py` — turns whatever we are given into one normalised bundle per case.
- `tools/` — property, tenancy, repair history, contractors, tickets, scheduling,
  messaging, landlord approval, escalation, voice. Adapter pattern: real API if
  configured, local mock otherwise. Agent code never changes.
- `policy/maintenance_policy.md` — UK maintenance rules, urgency bands, safety
  rules, approval limits, escalation triggers. The agent's ground truth.
- `agent.py` — understand -> triage -> plan -> act -> verify -> report.
  Conflict/gap check before acting. Decides proceed / ask / escalate.
- `runner.py` — parallel, per-case timeout, retries, fallback answer on any
  failure, trace per case. This is the coverage score.
- `writer.py` — fixed ANSWER.md / REASONING.md structure.
- `llm/` — Anthropic client + a deterministic mock LLM so the pipeline runs
  end to end with no API key.
- Voice (`tools/voice.py`) — ElevenLabs STT for call recordings; outbound
  confirmation call to contractor via ElevenLabs Conversational AI. Mocked in
  batch mode unless configured, so the Reality Test never depends on a live call.

## Roles tomorrow (3 people)

- **A — Runner & tools:** wire real data formats + event APIs into ingest/tools,
  own the 16:30 run, commits, hash, submission form.
- **B — Agent & policy:** prompt, policy doc, conflict/escalation behaviour,
  local eval on sample cases, hunt judgement errors.
- **C — Voice, demo, README:** ElevenLabs integration, demo video, README,
  SUBMISSION.md, LinkedIn/X posts.

## Timeline

- 09:30 onboarding — capture data formats, provided tools/APIs, submission form,
  answer-format hints. Paste everything into the repo under `docs/event/`.
- 10:00–10:30 read data, list case types, extract landlord instructions into policy.
- 10:30–12:00 loaders + tool adapters on real data; one case end to end.
- 12:00–13:30 run all sample cases, grade, fix judgement errors.
- 13:30–15:00 harden runner, voice tool, our own nasty cases.
- 15:00–16:15 README, LICENSE, SUBMISSION.md, clean-clone dry run, record video,
  draft posts.
- 16:30 **Reality Test**: run immediately, watch logs, commit ANSWERS, push, note hash.
  Touch no code.
- 17:00 submit form; publish posts.

See `docs/DAY_RUNBOOK.md` for the checklist version.

---

## Day plan v2 (written 10:45, 10 Oct, after reading the public cases and the Hacker Guide)

What we learned: cases are Dwelly's own anonymised ops records (index.md + history.md + attachments),
mundane repairs run through a fixed lifecycle, and the Reality Test is "pick the case up where the
history ends and do the next right things". Scoring: outcomes+coverage 38.5, judgement 14,
engineering 10.5, real-world 7, demo 30.

### Now, before the key arrives (no model needed)
1. **Case clock.** Tell the agent the "current date" is the last event's timestamp, not today.
   Chase dates, warranty ages and "3 days without reply" all depend on it.
2. **Nested folders.** If the Reality Test folder is `Property Management/001/...` or a zip, discover it.
3. **Status line in ANSWER.md.** Surface the last `update_case_status` call at the top:
   "Case status now: On hold, waiting for landlord, chase 13 Oct".
4. **Run summary in INDEX.md.** Decisions breakdown, escalation rate, tool failures recovered,
   estimated human minutes saved. This is the "real-world value" evidence and the demo's last shot.
5. **Model fallback.** If a case fails on API errors, retry once on a second model
   (ANTHROPIC_FALLBACK_MODEL) before writing the fallback answer.
6. **Preflight command.** `resolve preflight --cases X`: counts cases, ingests everything, estimates
   tokens, recommends workers and timeout for a 20-minute finish, checks the key works.
7. **Mine the public histories** for the agency's standard messages (landlord approval email,
   tenant "provider will attend" email, SMS wording, hold reasons) and put them into the policy as
   templates, so our outputs read like theirs.

### When the key arrives
8. One real case: `run --only 02_gas_smell --provider anthropic`. Read the trace.
9. Rate-limit test: all 9 samples with 6 workers. Pick workers/effort from what the API allows.
10. Decision-point eval: cut public cases at 2 points each (intake; after landlord reply), run the
    real model on ~15, compare with the hidden tail by eye, fix policy and prompt, not cases.

### Midday
11. Harden: inject tool failures and timeouts on the real model; confirm fallback answers.
12. Voice (person C only): ElevenLabs contractor-confirmation call from the real tool loop; TTS
    fallback. Never on the Reality Test path.

### 15:00 to 16:15 package, 16:30 run, 17:00 submit (unchanged runbook)
