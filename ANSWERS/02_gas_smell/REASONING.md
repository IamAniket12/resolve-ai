# Case 02_gas_smell — Reasoning and trace

## What the system received
- call_transcript.txt (transcript, 647 chars)
- crm_record.json (json, 351 chars)

## How the decision was reached
Rule-based mock: classified by keywords, verified property, applied safety/approval rules from policy, booked first available contractor from preferred list.

## Timeline of actions
### 1. `lookup_property` — OK (step 1, 0 ms)
Input:
```json
{
  "query": "PROP-0077"
}
```
Result:
```
{"found": true, "property_id": "PROP-0077", "address": "9 Birch Close, Croydon", "postcode": "CR0 7EX", "type": "house (3-bed semi)", "landlord_id": "LL-0220", "landlord_name": "Marcus Oyelaran", "landlord_phone": "+44 7700 900220", "landlord_email": "m.oyelaran@example.com", "landlord_instructions": "Do NOT spend more than £150 on anything without my written approval. I'm abroad until 20 Oct; email only.", "spend_limit_gbp": 150, "preferred_contractors": [], "gas_safety_cert_expiry": "2026-09-30", "eicr_expiry": "2028-01-15", "boiler": {"make": "Baxi 830", "installed": "2014-11", "age_years": 11}, "notes": "Gas safety certificate EXPIRED 2026-09-30 - renewal overdue."}
```

### 2. `lookup_tenancy` — OK (step 2, 0 ms)
Input:
```json
{
  "property_id": "PROP-0077"
}
```
Result:
```
{"tenancies": [{"tenancy_id": "TEN-5002", "property_id": "PROP-0077", "status": "active", "tenants": [{"name": "Tom Reilly", "phone": "+44 7700 900502", "email": "tom.reilly@example.com"}, {"name": "Sadie Reilly", "phone": "+44 7700 900503", "email": ""}], "start": "2024-02-15", "end": "2026-02-14", "rolling": true, "vulnerability_notes": "", "access_notes": "Both tenants work; access after 5pm or Saturdays."}], "active_tenancy": {"tenancy_id": "TEN-5002", "property_id": "PROP-0077", "status": "active", "tenants": [{"name": "Tom Reilly", "phone": "+44 7700 900502", "email": "tom.reilly@example.com"}, {"name": "Sadie Reilly", "phone": "+44 7700 900503", "email": ""}], "start": "2024-02-15", "end": "2026-02-14", "rolling": true, "vulnerability_notes": "", "access_notes": "Both tenants work; access after 5pm or Saturdays."}, "warning": null}
```

### 3. `get_repair_history` — OK (step 2, 0 ms)
Input:
```json
{
  "property_id": "PROP-0077"
}
```
Result:
```
{"property_id": "PROP-0077", "jobs": [{"job_id": "JOB-8650", "property_id": "PROP-0077", "date": "2026-03-02", "category": "plumbing", "description": "Dripping bath tap; washer replaced.", "contractor_id": "CON-RP03", "cost_gbp": 95, "outcome": "completed"}, {"job_id": "JOB-8700", "property_id": "PROP-0077", "date": "2025-09-28", "category": "gas", "description": "Annual gas safety check (CP12 issued, expires 2026-09-30).", "contractor_id": "CON-GS02", "cost_gbp": 80, "outcome": "completed"}], "count": 2}
```

### 4. `send_message` — OK (step 3, 0 ms)
Input:
```json
{
  "recipient_type": "tenant",
  "recipient": "+44 7700 900502",
  "channel": "sms",
  "body": "Open windows, do not use switches or naked flames, leave the property if the smell is strong, and call the National Gas Emergency line on 0800 111 999 now."
}
```
Result:
```
{"message_id": "MSG-9EEB35", "status": "delivered"}
```

### 5. `escalate_to_human` — OK (step 3, 0 ms)
Input:
```json
{
  "ticket_id": "",
  "severity": "critical",
  "to": "property_manager",
  "reason": "gas safety rule - requires certified engineer and human oversight.",
  "handover": "Property PROP-0077 (9 Birch Close, Croydon). Reported: gas hazard. Tenant advised (Open windows, do not use switches or naked flames, leave the property if the smell is strong, and call the National Gas Emergency line on 0800 111 999 now.). Needs Gas Safe engineer today; landlord Marcus Oyelaran to be informed."
}
```
Result:
```
{"escalation_id": "ESC-850B85", "status": "queued", "to": "property_manager", "severity": "critical"}
```

### 6. `send_message` — OK (step 3, 0 ms)
Input:
```json
{
  "recipient_type": "landlord",
  "recipient": "m.oyelaran@example.com",
  "channel": "email",
  "body": "Emergency gas report at 9 Birch Close, Croydon. Tenant advised on safety steps; property manager escalated; certified engineer being arranged."
}
```
Result:
```
{"message_id": "MSG-A79C94", "status": "delivered"}
```

## Agent notes during the run
- Verifying the property record.
- Checking tenancy and repair history.
- Safety rule applies; escalating and advising the tenant.
- Escalated under safety policy; tenant and landlord informed.

## Run metadata
- Provider/model: mock / mock-rules-v1
- Steps: 4
- Started: 2026-10-10T10:17:53+00:00  Finished: 2026-10-10T10:17:53+00:00
- Status: completed
- Token usage: n/a
