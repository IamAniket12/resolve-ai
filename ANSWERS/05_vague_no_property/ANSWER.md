# Case 05_vague_no_property — Answer

**Case status now:** awaiting tenant — Waiting for Tenant: unknown number +44 7700 900999 reported "broken again", no property or fault given. Asked for address, name and details by SMS (MSG-F4EE29). If no reply, chase Mon 13 Oct 2026 (try a call). Treat as emergency if the reply describes a safety issue.  
**Decision:** `needs_information`  
**Urgency:** `unclear`  
**Issue category:** unclear  
**Confidence:** 0.90  
**Processing status:** completed

## Summary
On Fri 10 Oct 2026 at 09:05 a text came from +44 7700 900999, a number not in the CRM: 'hi its broken again can u send someone. same as last time.' It gives no name, property or description of the fault. The property records search returned nothing and the case file has no address, so neither the property nor the reporter can be identified and no repair can be raised.

## Outcome
No ticket raised and nothing booked because no property can be identified. I texted the sender for their name, address/postcode, fault details, a photo and the date of the last repair, with emergency safety advice, and put the case on hold waiting for the tenant with a chase on Mon 13 Oct 2026.

## Actions taken
- lookup_property using the sender's phone number +44 7700 900999: no record found
- send_message SMS to +44 7700 900999 asking for name, property address/postcode, fault description/photo and date of last repair, with gas/CO (0800 111 999), 999 and water-near-electrics safety advice: delivered (MSG-F4EE29)
- record_note internal case note on the unidentified sender, the empty lookup, why no ticket was raised, and the possible repeat fault (NOTE-12A434)
- update_case_status to awaiting_tenant with chase date Mon 13 Oct 2026 (STS-4C4832)

## Failed actions and recovery
- None

## Escalation
- Required: **no**

## Conflicts in the information
- No conflicting information found

## Information gaps
- Property address/ID unknown: case file has none and the lookup on the phone number found nothing. Asked the sender by SMS; blocks everything else.
- Reporter's identity unknown: number not in CRM. Asked for full name; must be checked against the tenancy record once the property is known.
- Nature of the fault unknown ('it's broken'). Asked for a description and photo; urgency cannot be set until known.
- Previous repair ('same as last time') unknown: repair history can't be checked without a property ID. Asked for the last repair date; check the 90-day warranty/callback once identified.
- Access arrangements, pets and vulnerability unknown; to be gathered after the property is identified.

## Assumptions
- The sender is probably a current tenant reporting a repeat fault, but this is not verified and nothing has been acted on because of it.
- The case material is current (10 Oct 2026 = now) for the chase date.

## Communication
- Tenant: SMS to +44 7700 900999 (delivered, MSG-F4EE29): we don't have the number on file. It asks for full name, property address and postcode, what is broken and what it's doing now (photo helpful), and roughly when it was last repaired. It also gives safety advice: for a gas smell or CO alarm, open windows, don't use switches, leave and call 0800 111 999; for fire, flooding or risk to life, call 999; for water near electrics, switch off at the fuse box if safe.
- Landlord: none - landlord cannot be identified until the property is known.

## Risk flags
- Unverified sender: number not in CRM; check identity and tenancy before booking or sharing any property or personal details.
- Possible repeat fault ('broken again', 'same as last time'): may be under warranty/callback; check the history once the property is known.
- Unknown fault severity: could be a safety issue; safety advice sent and urgency to be raised immediately if the reply shows a hazard.

## Next steps
- Watch for the reply to MSG-F4EE29; if none by Mon 13 Oct 2026, call +44 7700 900999 to get the property and fault details.
- When they reply: look up the property and tenancy and check the sender is a current tenant before acting.
- Check the repair history for the previous job; if the same fault was repaired within 90 days, send it back to the original contractor under warranty/callback and flag it as recurring (3+ repairs in 12 months means recommending a replacement assessment).
- Raise a maintenance ticket with the correct category and urgency; if any safety issue (gas, CO, electrics, flooding, no heating/water for a vulnerable household) treat as emergency at once.
- Follow the normal steps: landlord approval (unless emergency or within the £250 pre-authorised limit), contractor selection, tenant notice of access.
- If the sender stays silent after repeated chases, escalate to the property manager.
