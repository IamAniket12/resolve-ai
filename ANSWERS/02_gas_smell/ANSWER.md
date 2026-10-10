# Case 02_gas_smell — Answer

**Case status now:** escalated to property_manager  
**Decision:** `escalated`  
**Urgency:** `emergency`  
**Issue category:** gas  
**Confidence:** 0.60  
**Processing status:** completed

## Summary
Reported gas issue at 9 Birch Close, Croydon. Urgency assessed as emergency. Evidence: "Caller: Hi, it's Tom Reilly at 9 Birch Close in Croydon. There's a really strong smell of gas in the kitchen this morning, near the cooker. My wife's got a headache. I've opened the back door."

## Outcome
Escalated to a human with handover: gas safety rule - requires certified engineer and human oversight.

## Actions taken
- send_message: {"recipient_type": "tenant", "recipient": "+44 7700 900502", "channel": "sms", "body": "Open windows, do not use switches or naked flames, leave the property if
- send_message: {"recipient_type": "landlord", "recipient": "m.oyelaran@example.com", "channel": "email", "body": "Emergency gas report at 9 Birch Close, Croydon. Tenant advise
- escalate_to_human: {"ticket_id": "", "severity": "critical", "to": "property_manager", "reason": "gas safety rule - requires certified engineer and human oversight.", "handover": 

## Failed actions and recovery
- None

## Escalation
- Required: **yes**
- To: property_manager
- Reason: gas safety rule - requires certified engineer and human oversight.

### Handover for the human
Property PROP-0077 (9 Birch Close, Croydon). Reported: gas hazard. Tenant advised (Open windows, do not use switches or naked flames, leave the property if the smell is strong, and call the National Gas Emergency line on 0800 111 999 now.). Needs Gas Safe engineer today; landlord Marcus Oyelaran to be informed.

## Conflicts in the information
- No conflicting information found

## Information gaps
- None

## Assumptions
- Mock LLM: keyword triage; replace with Claude for real judgement.

## Communication
- Tenant: Open windows, do not use switches or naked flames, leave the property if the smell is strong, and call the National Gas Emergency line on 0800 111 999 now.
- Landlord: Emergency gas report at 9 Birch Close, Croydon. Tenant advised on safety steps; property manager escalated; certified engineer being arranged.

## Risk flags
- gas safety rule applied

## Next steps
- Human reviews escalation
