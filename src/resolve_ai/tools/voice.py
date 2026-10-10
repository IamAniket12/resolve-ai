"""ElevenLabs integration: speech-to-text for call recordings, outbound confirmation
calls through a Conversational AI agent, and text-to-speech for tenant voice updates.

Everything degrades to a simulation when keys are missing or VOICE_LIVE_CALLS=0, so the
batch run never depends on a live phone call.

Endpoints to verify against the ElevenLabs docs on the day:
  POST https://api.elevenlabs.io/v1/speech-to-text                 (model_id=scribe_v1)
  POST https://api.elevenlabs.io/v1/convai/twilio/outbound-call     (agent_id, agent_phone_number_id, to_number)
  GET  https://api.elevenlabs.io/v1/convai/conversations/{id}       (transcript + analysis)
  POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict

import requests

from resolve_ai.config import Settings

log = logging.getLogger(__name__)
API = "https://api.elevenlabs.io/v1"


def transcribe_file(path: Path, api_key: str) -> str:
    with open(path, "rb") as f:
        r = requests.post(
            f"{API}/speech-to-text",
            headers={"xi-api-key": api_key},
            files={"file": (path.name, f)},
            data={"model_id": "scribe_v1", "diarize": "true", "tag_audio_events": "false"},
            timeout=300,
        )
    r.raise_for_status()
    data = r.json()
    # Prefer diarised words if present, else plain text
    words = data.get("words")
    if words and any(w.get("speaker_id") for w in words):
        lines, cur, buf = [], None, []
        for w in words:
            if w.get("type") == "spacing":
                continue
            sp = w.get("speaker_id", "speaker")
            if sp != cur and buf:
                lines.append(f"{cur}: {''.join(buf).strip()}")
                buf = []
            cur = sp
            buf.append(w.get("text", "") + " ")
        if buf:
            lines.append(f"{cur}: {''.join(buf).strip()}")
        return "\n".join(lines)
    return data.get("text", "")


def make_transcriber(settings: Settings):
    if not settings.elevenlabs_api_key:
        return None
    return lambda p: transcribe_file(p, settings.elevenlabs_api_key)


def text_to_speech(settings: Settings, text: str, out_path: Path, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Path:
    r = requests.post(
        f"{API}/text-to-speech/{voice_id}",
        headers={"xi-api-key": settings.elevenlabs_api_key, "accept": "audio/mpeg"},
        json={"text": text, "model_id": "eleven_turbo_v2_5"},
        timeout=120,
    )
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return out_path


def place_call(settings: Settings, *, to_role: str, phone: str, purpose: str, talking_points: str, case_id: str) -> Dict[str, Any]:
    live = settings.voice_live_calls and settings.elevenlabs_api_key and settings.elevenlabs_agent_id and settings.elevenlabs_phone_number_id
    if not live:
        return _simulated_call(to_role, phone, purpose, talking_points)
    try:
        r = requests.post(
            f"{API}/convai/twilio/outbound-call",
            headers={"xi-api-key": settings.elevenlabs_api_key},
            json={
                "agent_id": settings.elevenlabs_agent_id,
                "agent_phone_number_id": settings.elevenlabs_phone_number_id,
                "to_number": phone,
                "conversation_initiation_client_data": {
                    "dynamic_variables": {"purpose": purpose, "talking_points": talking_points, "case_id": case_id, "to_role": to_role}
                },
            },
            timeout=60,
        )
        r.raise_for_status()
        conv_id = r.json().get("conversation_id")
        summary = _wait_for_conversation(settings, conv_id) if conv_id else {}
        return {"status": "completed", "mode": "live", "conversation_id": conv_id, **summary}
    except Exception as e:  # noqa: BLE001
        log.warning("live call failed: %s", e)
        return {"status": "failed", "mode": "live", "error": str(e), "fallback": "send a message instead"}


def _wait_for_conversation(settings: Settings, conv_id: str, timeout_s: int = 240) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(f"{API}/convai/conversations/{conv_id}", headers={"xi-api-key": settings.elevenlabs_api_key}, timeout=30)
        if r.ok and r.json().get("status") in {"done", "ended", "completed"}:
            d = r.json()
            transcript = "\n".join(f"{t.get('role')}: {t.get('message')}" for t in d.get("transcript", []))
            return {"transcript": transcript, "analysis": d.get("analysis", {})}
        time.sleep(5)
    return {"transcript": "", "note": "call still in progress when timeout reached"}


def _simulated_call(to_role: str, phone: str, purpose: str, talking_points: str) -> Dict[str, Any]:
    """Honest stand-in when telephony is not configured: no call is placed and nothing is confirmed.
    The agent must treat this as 'no contact made' and reach the person another way or hand the call to a human."""
    return {
        "status": "not_placed",
        "mode": "simulated",
        "to_role": to_role,
        "phone": phone,
        "purpose": purpose,
        "transcript_summary": "",
        "note": ("No live call was placed: voice calling is not enabled in this environment. Nobody was reached, nothing was "
                 "confirmed and no commitment exists. Use send_message to reach this person, and if a live conversation is "
                 "essential, record in the handover that a human must make the call."),
    }
get(to_role, "Call completed.")
    return {
        "status": "completed",
        "mode": "simulated",
        "to_role": to_role,
        "phone": phone,
        "purpose": purpose,
        "transcript_summary": confirm,
        "note": "Simulated call (VOICE_LIVE_CALLS=0 or ElevenLabs not configured).",
    }
