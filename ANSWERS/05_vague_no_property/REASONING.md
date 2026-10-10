# Case 05_vague_no_property — Reasoning and trace

## What the system received
- sms.txt (text, 146 chars)

## How the decision was reached
Rule-based mock: classified by keywords, verified property, applied safety/approval rules from policy, booked first available contractor from preferred list.

## Timeline of actions
### 1. `escalate_to_human` — OK (step 1, 0 ms)
Input:
```json
{
  "ticket_id": "",
  "severity": "medium",
  "to": "property_manager",
  "reason": "Reporter did not identify the property and no match could be derived.",
  "handover": "Message received with no property ID/address. Ask reporter for address/postcode, then triage per policy."
}
```
Result:
```
{"escalation_id": "ESC-97432F", "status": "queued", "to": "property_manager", "severity": "medium"}
```

## Agent notes during the run
- No property identifier found in the material; I cannot verify the property.
- Escalated; nothing further can be done safely.

## Run metadata
- Provider/model: mock / mock-rules-v1
- Steps: 2
- Started: 2026-10-10T10:11:26+00:00  Finished: 2026-10-10T10:11:26+00:00
- Status: completed
- Token usage: n/a
