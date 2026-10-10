# Case 09_ambiguous_no_hot_water — Reasoning and trace

## What the system received
- crm_record.json (json, 321 chars)
- portal_ticket.json (json, 465 chars)

## How the decision was reached
Rule-based mock: classified by keywords, verified property, applied safety/approval rules from policy, booked first available contractor from preferred list.

## Timeline of actions
### 1. `lookup_property` — OK (step 1, 0 ms)
Input:
```json
{
  "query": "PROP-0233"
}
```
Result:
```
{"found": true, "property_id": "PROP-0233", "address": "5 Stanley Terrace, Nottingham", "postcode": "NG7 1AB", "type": "house (2-bed terrace)", "landlord_id": "LL-0702", "landlord_name": "Graham Steele", "landlord_phone": "+44 7700 900702", "landlord_email": "g.steele@example.com", "landlord_instructions": "Standard authority.", "spend_limit_gbp": 250, "preferred_contractors": [], "gas_safety_cert_expiry": "2027-04-10", "eicr_expiry": "2028-05-20", "boiler": {"make": "Worcester Greenstar 30i combi", "installed": "2022-03", "age_years": 4}, "notes": "Bathroom has a Triton electric shower on its own circuit; the combi boiler supplies hot water to the taps only. Water stopcock under stairs."}
```

### 2. `lookup_tenancy` — OK (step 2, 0 ms)
Input:
```json
{
  "property_id": "PROP-0233"
}
```
Result:
```
{"tenancies": [{"tenancy_id": "TEN-5013", "property_id": "PROP-0233", "status": "active", "tenants": [{"name": "Mo Hussain", "phone": "+44 7700 900631", "email": "mo.hussain@example.com"}], "start": "2026-02-01", "end": "2027-01-31", "rolling": false, "vulnerability_notes": "", "access_notes": "Shift worker; prefers text. Available mornings before 11."}], "active_tenancy": {"tenancy_id": "TEN-5013", "property_id": "PROP-0233", "status": "active", "tenants": [{"name": "Mo Hussain", "phone": "+44 7700 900631", "email": "mo.hussain@example.com"}], "start": "2026-02-01", "end": "2027-01-31", "rolling": false, "vulnerability_notes": "", "access_notes": "Shift worker; prefers text. Available mornings before 11."}, "warning": null}
```

### 3. `get_repair_history` — OK (step 2, 0 ms)
Input:
```json
{
  "property_id": "PROP-0233"
}
```
Result:
```
{"property_id": "PROP-0233", "jobs": [{"job_id": "JOB-8755", "property_id": "PROP-0233", "date": "2026-06-02", "category": "heating", "description": "Annual boiler service. No faults.", "contractor_id": "CON-TP12", "cost_gbp": 80, "outcome": "completed"}], "count": 1}
```

### 4. `create_maintenance_ticket` — OK (step 3, 0 ms)
Input:
```json
{
  "property_id": "PROP-0233",
  "title": "heating issue reported",
  "category": "heating",
  "urgency": "urgent",
  "description": "Case ID: 09_ambiguous_no_hot_water\nSource: data/sample_cases/09_ambiguous_no_hot_water\nFiles received (2): crm_record.json (json), portal_ticket.json (json)\nCase date: 2026-10-10 07:55. Treat this as \"now\" for ages, deadlines, chase dates and how long people have been waiting; today's real date is irrelevant.\n\nWork this case now. Use the tools to verify and act. When you have finished acting (or determined that you must stop), end your turn with a short plain-text summary of the outcome.\n\n<case_material>\n<<<FILE name=\"crm_record.json\" kind=\"json\">>>\n{\n  \"property_id\": \"PROP-0233\",\n  \"address\": \"5 Stanley Terrace, Nottingham NG7 1AB\",\n  \"tenancy_id\": \"TEN-5013\",\n  \"property_notes\": \"Bathroom has a Triton electric shower on its own circuit. Combi boiler supplies hot water to the taps only, n",
  "reported_by": "Mo Hussain"
}
```
Result:
```
{"ticket_id": "TKT-9F31F9", "property_id": "PROP-0233", "title": "heating issue reported", "category": "heating", "urgency": "urgent", "description": "Case ID: 09_ambiguous_no_hot_water\nSource: data/sample_cases/09_ambiguous_no_hot_water\nFiles received (2): crm_record.json (json), portal_ticket.json (json)\nCase date: 2026-10-10 07:55. Treat this as \"now\" for ages, deadlines, chase dates and how long people have been waiting; today's real date is irrelevant.\n\nWork this case now. Use the tools to verify and act. When you have finished acting (or determined that you must stop), end your turn with a short plain-text summary of the outcome.\n\n<case_material>\n<<<FILE name=\"crm_record.json\" kind=\"json\">>>\n{\n  \"property_id\": \"PROP-0233\",\n  \"address\": \"5 Stanley Terrace, Nottingham NG7 1AB\",\n  \"tenancy_id\": \"TEN-5013\",\n  \"property_notes\": \"Bathroom has a Triton electric shower on its own circuit. Combi boiler supplies hot water to the taps only, n", "reported_by": "Mo Hussain", "status": "open", "created_at": "2026-10-10T11:17:53"}
```

### 5. `send_message` — OK (step 4, 0 ms)
Input:
```json
{
  "recipient_type": "tenant",
  "recipient": "+44 7700 900631",
  "channel": "sms",
  "body": "Quick check so we send the right engineer today: is the hot water from the KITCHEN tap also cold? If the kitchen tap runs hot, the fault is the electric shower unit and we will send an electrician. If it is cold too, it is the boiler and we will send a Gas Safe engineer. Reply 'tap hot' or 'tap cold'."
}
```
Result:
```
{"message_id": "MSG-852257", "status": "delivered"}
```

### 6. `record_note` — OK (step 4, 0 ms)
Input:
```json
{
  "ticket_id": "TKT-9F31F9",
  "note": "Awaiting tenant reply: kitchen tap hot/cold decides electrician vs gas engineer. Provisional trade: gas_engineer."
}
```
Result:
```
{"note_id": "NOTE-6157CD", "status": "saved"}
```

## Agent notes during the run
- Verifying the property record.
- Checking tenancy and repair history.
- Cannot tell whether the shower unit or the boiler failed; asking one question before booking.
- Ticket open; awaiting the tenant's answer before booking.

## Run metadata
- Provider/model: mock / mock-rules-v1
- Steps: 5
- Started: 2026-10-10T10:17:53+00:00  Finished: 2026-10-10T10:17:53+00:00
- Status: completed
- Token usage: n/a
