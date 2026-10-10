# Case 09_ambiguous_no_hot_water — Answer

**Case status now:** needs information  
**Decision:** `needs_information`  
**Urgency:** `urgent`  
**Issue category:** heating  
**Confidence:** 0.60  
**Processing status:** completed

## Summary
Reported heating issue at 5 Stanley Terrace, Nottingham. Urgency assessed as urgent. Evidence: ""property_notes": "Bathroom has a Triton electric shower on its own circuit. Combi boiler supplies hot water to the taps only, not the shower.","

## Outcome
Blocked pending information: Whether the kitchen hot tap is also cold - decides electric shower (electrician) vs boiler (Gas Safe engineer)

## Actions taken
- create_maintenance_ticket: {"property_id": "PROP-0233", "title": "heating issue reported", "category": "heating", "urgency": "urgent", "description": "Case ID: 09_ambiguous_no_hot_water\n
- send_message: {"recipient_type": "tenant", "recipient": "+44 7700 900631", "channel": "sms", "body": "Quick check so we send the right engineer today: is the hot water from t
- record_note: {"ticket_id": "TKT-9F31F9", "note": "Awaiting tenant reply: kitchen tap hot/cold decides electrician vs gas engineer. Provisional trade: gas_engineer."}

## Failed actions and recovery
- None

## Escalation
- Required: **no**

## Conflicts in the information
- No conflicting information found

## Information gaps
- Whether the kitchen hot tap is also cold - decides electric shower (electrician) vs boiler (Gas Safe engineer)

## Assumptions
- Mock LLM: keyword triage; replace with Claude for real judgement.

## Communication
- Tenant: Quick check so we send the right engineer today: is the hot water from the KITCHEN tap also cold? If the kitchen tap runs hot, the fault is the electric shower unit and we will send an electrician. If it is cold too, it is the boiler and we will send a Gas Safe engineer. Reply 'tap hot' or 'tap cold'.
- Landlord: none

## Risk flags
- None

## Next steps
- Await approval / information
