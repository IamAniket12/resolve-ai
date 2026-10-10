# Case 07_noisy_group_chat — Answer

**Case status now:** in progress  
**Decision:** `in_progress`  
**Urgency:** `urgent`  
**Issue category:** damp_mould  
**Confidence:** 0.60  
**Processing status:** completed

## Summary
Reported damp_mould issue at 14 Linden Grove, Leeds. Urgency assessed as urgent. Evidence: "[17/09/2026, 14:06] Priya: btw the bathroom extractor fan has stopped working completely, it's not just noisy any more. the ceiling above the shower has black mould patches now, it's spreading onto the wall"

## Outcome
Contractor booked and parties informed.

## Actions taken
- create_maintenance_ticket: {"property_id": "PROP-0188", "title": "damp_mould issue reported", "category": "damp_mould", "urgency": "urgent", "description": "Case ID: 07_noisy_group_chat\n
- schedule_contractor: {"ticket_id": "TKT-C94980", "contractor_id": "CON-DS08", "slot_id": "SLOT-URG-1", "access_notes": "Someone usually home after 4pm; WhatsApp group is the agreed 
- send_message: {"recipient_type": "tenant", "recipient": "+44 7700 900611", "channel": "sms", "body": "Hi Josh Carter, we've booked DryHome Damp Specialists for 2026-10-12T09:
- send_message: {"recipient_type": "landlord", "recipient": "f.begum@example.com", "channel": "email", "body": "Damp_Mould repair logged at 14 Linden Grove, Leeds (ticket TKT-C

## Failed actions and recovery
- None

## Escalation
- Required: **no**

## Conflicts in the information
- No conflicting information found

## Information gaps
- None

## Assumptions
- Mock LLM: keyword triage; replace with Claude for real judgement.
- Material is long and mostly irrelevant chatter; only maintenance-related lines were used.

## Communication
- Tenant: Hi Josh Carter, we've booked DryHome Damp Specialists for 2026-10-12T09:00 (ref BKG-D621D4). They will call before arriving. Reply if that time doesn't work.
- Landlord: Damp_Mould repair logged at 14 Linden Grove, Leeds (ticket TKT-C94980); DryHome Damp Specialists booked for 2026-10-12T09:00, est. £180.

## Risk flags
- possible tenant-caused damage, recharge to consider: "[20/09/2026, 18:49] Priya: also I need to own up - I dropped the cast iron pan on the hob yesterday and the glass has a big crack across the back left ring. the other rings work but I'm not using the cracked one. sorry 🙈"

## Next steps
- Contractor attends; confirm completion with tenant
