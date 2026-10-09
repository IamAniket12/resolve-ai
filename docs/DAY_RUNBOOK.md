# Day Runbook — 10 Oct 2026

## Before leaving home
- [ ] Laptop charged, charger, phone hotspot as WiFi backup
- [ ] `git clone` works from a clean folder; `python -m resolve_ai run --cases data/sample_cases --provider mock` passes
- [ ] GitHub repo created (public, Apache 2.0) — or ready to create at the event
- [ ] LinkedIn + X accounts logged in on at least one phone

## 09:30 Onboarding — capture into docs/event/
- [ ] Exact data layout of the synthetic environment (folders, file types)
- [ ] Tools/APIs provided (base URL, auth, endpoints, docs) -> `tools/http_backend.py`
- [ ] Submission form fields; required ANSWER.md shape if they specify one
- [ ] API keys: ANTHROPIC_API_KEY, ELEVENLABS_API_KEY -> `.env` (never commit)
- [ ] Ask: will Reality Test cases arrive in the same format? Same tools?

## 10:00–10:30 Understand
- [ ] `python -m resolve_ai inspect --cases <data>` — confirm every file loads
- [ ] List case types seen; note conflicts/missing-info patterns in the data
- [ ] Copy landlord instructions / SLAs / approval limits into `policy/maintenance_policy.md`

## 10:30–12:00 Wire
- [ ] Ingest handles every real file type
- [ ] Each tool mapped to a real API or kept on mock (document which in README)
- [ ] One real case end to end with `--provider anthropic`

## 12:00–13:30 Judgement
- [ ] Run all provided cases; read every ANSWER.md
- [ ] Add expectations to `eval/expectations.json`; `python -m resolve_ai grade`
- [ ] Fix prompt/policy, not per-case hacks

## 13:30–15:00 Harden
- [ ] Inject failures (tool errors, timeouts) and confirm fallback answers are written
- [ ] Workers/timeouts tuned so N cases finish in < 15 min
- [ ] Voice: STT on a call file; outbound call demo works (or TTS fallback)

## 15:00–16:15 Package
- [ ] README 8 sections complete, `.env.example` accurate
- [ ] Clean clone -> install -> run sample cases: passes
- [ ] Record 60s demo -> `demo/demo.mp4` (Git LFS if > 50MB)
- [ ] SUBMISSION.md filled; social posts drafted

## 16:30 Reality Test (NO CODE CHANGES)
- [ ] Drop cases into `data/reality_test/`
- [ ] `python -m resolve_ai run --cases data/reality_test --out ANSWERS --workers 8`
- [ ] Watch `logs/<run>/run.log`; confirm every case has ANSWER.md
- [ ] `git add ANSWERS logs && git commit -m "Reality Test results" && git push`
- [ ] Record commit hash -> submission form
- [ ] If a case fell back: leave it. Do not hand-edit answers.

## 17:00
- [ ] Submit form (repo URL, team, track, names, hash, results, video path, post URLs)
- [ ] Publish LinkedIn + X posts with repo link
