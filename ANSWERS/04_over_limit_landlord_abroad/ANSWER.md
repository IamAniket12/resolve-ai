# Case 04_over_limit_landlord_abroad — Answer

**Case status now:** awaiting landlord — Waiting for Landlord: written OK for overdue CP12 at GasSure's 12/10 visit (APR-AB2D9E). Escalated to compliance. Chase by email Sun 11/10 if no reply.  
**Decision:** `escalated`  
**Urgency:** `urgent`  
**Issue category:** heating/boiler (plus overdue gas safety certificate)  
**Confidence:** 0.80  
**Processing status:** completed

## Summary
Tenant Sadie Reilly reported through the portal on 09/10/2026 that the Baxi 830 boiler (2014) at 9 Birch Close, Croydon CR0 7EX (PROP-0077) has been banging loudly for a week and the upstairs radiators are cold, though hot water works. The landlord, Marcus Oyelaran, has a standing instruction: nothing over £150 without his written OK, he is abroad until 20 Oct, and contact is by email only. Checking the records showed the gas safety certificate (CP12) expired on 30/09/2026, which is an overdue legal requirement on an occupied property with a faulty gas boiler.

## Outcome
A Gas Safe engineer, GasSure London, is booked to diagnose and make safe on Mon 12/10/2026 09:00-11:00 (BKG-06E5F1, £140, within the landlord's £150 limit). The overdue gas safety check (TKT-333DB0) is waiting for the landlord's written approval (APR-AB2D9E) and has been escalated to compliance (ESC-9DEF56).

## Actions taken
- Looked up the property PROP-0077 and confirmed the landlord LL-0220, his £150 limit, email-only contact, and the gas safety certificate expiry of 2026-09-30.
- Looked up the tenancy: TEN-5002 is active and rolling (Tom and Sadie Reilly), with no vulnerability notes and access after 5pm or on Saturdays.
- Checked repair history: a bath tap in 03/2026 and the last gas safety check by GasSure (JOB-8700, 2025-09-28, £80). No previous heating repairs.
- Searched Gas Safe engineers for CR0: found Thames Heating (CON-TH01, £120) and GasSure London (CON-GS02, £140).
- Checked GasSure London's urgent availability: slots offered on Mon 12/10.
- Created ticket TKT-CA0F52 (heating, urgent).
- Called tenant Sadie Reilly (the call was simulated). The summary says she confirmed access and reported no new hazards.
- Booked GasSure London for SLOT-URG-1, Mon 12/10 09:00-11:00, booking BKG-06E5F1. Scope is diagnose and make safe only, capped at £150, with no further work without the landlord's written approval.
- Created ticket TKT-333DB0 for the overdue gas safety check.
- Requested landlord approval APR-AB2D9E: est. £80 for the gas safety check at the same visit, about £220 combined.
- Emailed the landlord about the booking within his limit and asked for written OK for the gas safety check (MSG-1B5C87).
- Sent Sadie an SMS confirming the appointment, with pets and gas-emergency advice (MSG-9DD9F5).
- Emailed the tenants via Tom Reilly's address confirming the appointment, with the same advice (MSG-CF9979).
- Emailed GasSure the job details, the £150 cap, and a request for their gas safety check price, with an instruction not to do the check until approval is confirmed (MSG-3C4B3D).
- Escalated the lapsed gas safety certificate to compliance at high severity (ESC-9DEF56).
- Set TKT-CA0F52 to appointment_booked and TKT-333DB0 to awaiting_landlord.
- Recorded an internal note on TKT-CA0F52 with the decisions and assumptions.

## Failed actions and recovery
- Checking Thames Heating's (CON-TH01) availability failed with HTTP 504 (gateway timeout). I retried once and it failed with 504 again. I switched to GasSure London (CON-GS02), which returned slots and was booked.

## Escalation
- Required: **yes**
- To: compliance
- Reason: The gas safety certificate expired on 30/09/2026 on an occupied property whose gas boiler is now faulty. The landlord's £150 written-approval rule and his email-only contact while abroad may stop the renewal from happening at Monday's visit.

### Handover for the human
PROPERTY: PROP-0077, 9 Birch Close, Croydon CR0 7EX. Active rolling tenancy TEN-5002: Tom Reilly (07700 900502, tom.reilly@example.com) and Sadie Reilly (07700 900503, no email on file). No vulnerabilities recorded. LANDLORD: Marcus Oyelaran (LL-0220, m.oyelaran@example.com). Nothing over £150 without his written OK, abroad until 20/10, EMAIL ONLY, no calls. REPAIR (TKT-CA0F52): banging Baxi 830 boiler with cold upstairs radiators, classed urgent. GasSure London (Gas Safe 598877, 020 7946 0102) is booked for Mon 12/10 09:00-11:00 (BKG-06E5F1, £140), diagnose and make safe only. Any repair over £150 needs the landlord's written approval by email. GAS SAFETY CHECK (TKT-333DB0): the certificate expired 30/09/2026. The last check was by GasSure on 28/09/2025 for £80. Approval APR-AB2D9E is pending: about £80 for the check plus £140 for the visit, about £220 in total. GasSure has been asked for its price and told not to do the check without our written confirmation. DECISION NEEDED: if the landlord has not replied in writing by Mon 12/10 09:00, decide whether the agency instructs the check anyway as a legal duty (the landlord cannot lawfully refuse it, and policy says escalate rather than refuse). Also review why the certificate lapsed and whether the tenants need to be told formally. RECOMMENDATION: chase the landlord by email on Sun 11/10. If he is still silent, get a manager's sign-off for GasSure to do the check on Monday and email the landlord the same day.

## Conflicts in the information
- The tenant described the problem as 'Not urgent', but policy classes partial loss of heating with a boiler fault as urgent. — *Followed policy and classed it urgent, with a contractor within 3 working days. The tenant's view does not set the band.*
- Access notes in the records say the tenants are only available after 5pm or on Saturdays. GasSure only offered weekday daytime slots on 12/10. — *Called the tenant to confirm access. The summary says she confirmed the access arrangement, so I booked 09:00-11:00. The SMS and email name the slot and ask her to contact GasSure if it doesn't suit.*
- The landlord's email shows a garbled currency symbol ('��150'). — *Trusted the property record, which shows a £150 limit and the same instruction.*

## Information gaps
- The simulated call summary does not say which slot the tenant agreed to. I assumed the first slot and gave the time in writing so she can correct it.
- GasSure's current price for the gas safety check is unknown. I estimated £80 from last year and asked GasSure to confirm.
- The cause of the banging and the cost of the repair are unknown until diagnosis. Anything over £150 needs the landlord's written OK.
- Pets are unknown. The tenants were asked to tell the engineer.
- GasSure returned SLOT-URG-3 as a duplicate of SLOT-URG-1. I ignored it as a data quirk.

## Assumptions
- The landlord's standing £150 limit counts as pre-authorisation for the £140 diagnostic call-out, so no separate approval was needed before booking.
- The doing-the-check-at-the-same-visit plan is worth combining with the repair visit. Because the combined spend is over £150, I asked for the landlord's written OK rather than splitting the jobs to stay under his limit.
- The tenants can be contacted as a household: email to Tom, SMS to Sadie.

## Communication
- Tenant: Sadie was called (simulated) to confirm access and given safety advice. She was sent an SMS, and the tenants were emailed via Tom's address. Both messages confirm GasSure London (020 7946 0102) on Mon 12/10 09:00-11:00, ask them to mention pets and to contact GasSure if the time doesn't suit, say to turn the heating off if the banging gets worse, and give gas/CO emergency advice (0800 111 999).
- Landlord: By email only: he was told GasSure is booked for diagnosis at £140, within his £150 limit, and that no further work will be done without his written approval. He was told the gas safety certificate expired on 30/09 and asked for written OK to renew it at the same visit (about £220 total). Approval APR-AB2D9E is pending.

## Risk flags
- Gas safety certificate expired 30/09/2026 on an occupied property: a breach of the Gas Safety (Installation and Use) Regulations 1998.
- Faulty gas boiler (banging) with no current gas safety certificate. The tenants were given gas/CO emergency advice.
- The landlord's £150 written-approval limit and email-only contact while abroad until 20/10 may delay a legally required job.
- Temperatures are falling. Heating loss becomes an emergency from 1 Nov if it isn't fixed.

## Next steps
- Sun 11/10: if there's no reply to APR-AB2D9E, chase the landlord by email (two lines, email only).
- Compliance or a manager to decide by Mon 12/10 09:00 whether to instruct the gas safety check if the landlord is still silent.
- Mon 12/10: confirm with GasSure and the tenant that the visit went ahead. Get the findings, a quote, and the gas safety check price.
- If the repair quote is over £150, send the landlord the quote approval email and hold TKT-CA0F52 as waiting for landlord.
- Given the boiler's age (11 years), raise a replacement assessment with the landlord if the repair is expensive.
- Completion check: contractor confirms done, tenant confirms, invoice of £140 or less matches the booking, gas safety certificate uploaded.
