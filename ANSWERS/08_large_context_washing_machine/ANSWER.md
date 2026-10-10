# Case 08_large_context_washing_machine — Answer

**Case status now:** appointment booked — ApplianceFix SW callback BKG-842139 Mon 12 Oct 09-11 (concierge access). Waiting for Landlord: replacement approval APR-9BAE23 (£350), chase 13 Oct. Flat 6 ingress/insurance escalated to PM. Check engineer report/quote 12-13 Oct.  
**Decision:** `escalated`  
**Urgency:** `urgent`  
**Issue category:** appliance  
**Confidence:** 0.80  
**Processing status:** completed

## Summary
Tenant Grace Adeyemi reported that the landlord-supplied Beko WTK94121W washing machine at Flat 7, Riverside Court, Bristol BS1 6XY (PROP-0205) leaked badly again. Water pooled across the kitchen floor and went under the units; the machine is now switched off. This is the 4th fault in 12 months, and on 30 Aug ApplianceFix SW said the machine was beyond economical repair. The company landlord (Owen Pryce) said 'repair not replace, under the usual limit'. Separately, Wharf Lane Block Management report a wet ceiling patch in Flat 6 directly below, possibly from Flat 7, and say they may involve the freeholder's insurer.

## Outcome
ApplianceFix SW is booked for a callback/diagnosis visit on Mon 12 Oct 2026, 09:00-11:00 (BKG-842139), within the landlord's £250 limit. Landlord approval for a £350 replacement is pending (APR-9BAE23). The Flat 6 water damage and possible insurance claim were escalated to the property manager (ESC-124DEF).

## Actions taken
- Checked the property record PROP-0205, tenancy TEN-5012 (active, rolling) and repair history (3 prior washing machine jobs by CON-AF10).
- Created maintenance ticket TKT-365DCE (appliance, urgent).
- Searched the appliance engineer panel for BS1 6XY: only ApplianceFix South West (CON-AF10) returned.
- Called tenant Grace Adeyemi (simulated call): tenant confirmed the access arrangement and current state; no new hazards reported.
- Checked CON-AF10 urgent availability: slots on 12 Oct 2026.
- Booked CON-AF10 slot SLOT-URG-1 (Mon 12 Oct 09:00-11:00): booking BKG-842139, estimated £95. Booked as a callback on JOB-8798; concierge access; no chargeable work over £250 without approval.
- Raised landlord approval request APR-9BAE23 for a £350 replacement (pending).
- Emailed landlord Owen Pryce with the evidence (machine age, fault history, engineer's beyond-economical-repair finding, his own standing instruction, Flat 6 ingress) and asked for a written decision (MSG-6321BA).
- Emailed tenant: appointment confirmation, interim advice (keep unplugged, isolate the water valve, dry the floor, watch electrics), replacement pending landlord, mention pets (MSG-D75F61).
- Sent appointment SMS to tenant (MSG-30ADE3).
- Emailed job instructions to ApplianceFix SW: callback/warranty check, leak source, check under units, link to Flat 6, BER report and itemised replacement quote (MSG-C080E4).
- Emailed Wharf Lane Block Management confirming the investigation and visit date; findings to follow (MSG-F8C12F).
- Escalated to the property manager over Flat 6 third-party damage and the possible insurance claim (ESC-124DEF, medium).
- Set case status to appointment_booked with chase comment (STS-2D1447).
- Recorded an internal triage and conflicts note (NOTE-51CE31).

## Failed actions and recovery
- None

## Escalation
- Required: **yes**
- To: property manager
- Reason: Third-party water damage to Flat 6, with block management saying they may raise it with the freeholder's insurer (policy: insurance claims go to a human). The landlord's 'repair not replace' instruction also conflicts with the engineer's beyond-economical-repair finding and the landlord's own standing instruction, so a manager may need to talk to him if he refuses.

### Handover for the human
PROP-0205, Flat 7 Riverside Court, 3 Wharf Lane, Bristol BS1 6XY. Tenancy TEN-5012 is active and rolling (Grace Adeyemi +44 7700 900621, Sam Whitlock). The landlord-supplied Beko WTK94121W (new Mar 2024 per inventory KIT-09) leaked badly on 9 Oct and is unplugged and out of use. Fault history, all by ApplianceFix SW CON-AF10: brushes £120 (Nov-25), door seal £135 (May-26), pump housing leak temporary fix £110 (30 Aug-26). On 30 Aug the engineer wrote that the machine is beyond economical repair and recommended replacement at about £350. Landlord Owen Pryce (LL-0610, owen.pryce@rcinvest.example.com, +44 7700 900610) said repair only, under £250, and that the machine is 'about a year old' (wrong: about 2.5 years). His standing instruction on file allows replacement when an engineer says beyond economical repair. Block management (block@wharflane.example.com) report a wet Flat 6 kitchen ceiling, logged as RC-2004 on 14 Sep (possible ingress from Flat 7), and may involve the freeholder's insurer. DONE: ticket TKT-365DCE; CON-AF10 callback booked as BKG-842139, Mon 12 Oct 09:00-11:00, concierge access, est. £95; approval APR-9BAE23 (£350 replacement) pending; tenant, landlord, contractor and block management informed. No liability admitted. YOUR ACTIONS: (1) Handle the Flat 6 damage and any insurer contact; decide whether the landlord's insurer needs notifying and who pays for the ceiling repair. (2) If Owen refuses replacement after receiving the BER report, speak to him; repeated temporary fixes are costing more than a replacement and risk more leak damage. (3) If the engineer finds the machine is not the source of the Flat 6 ingress, book a plumber leak-trace (Flat 7 has had sealant renewed 3 times: RC-1000, RC-1036, RC-1054). RECOMMENDED: approve the replacement once the firm quote arrives, and send the engineer's findings and photos to block management.

## Conflicts in the information
- Landlord says the washing machine is 'only about a year old'. The check-in inventory (KIT-09) and repair history (JOB-8611) say it was supplied new in March 2024, about 2.5 years ago. — *Trusted the inventory and repair records (documentary, consistent with each other). Corrected the age in the email to the landlord.*
- Landlord instructs 'repair not replace, keep under the usual limit'. The engineer (30 Aug, JOB-8798) says the machine is beyond economical repair, and the landlord's standing instruction on file allows replacement in that case. — *Did not override the landlord. Booked only a callback/diagnosis visit within his £250 limit and raised a formal approval request (APR-9BAE23) for replacement with the evidence. Escalated to the PM in case he refuses.*
- Tenant says records might list the machine as a Bosch. Our property record, repair history, inventory and block log all say Beko WTK94121W. — *No conflict in our records; Beko confirmed. Told the tenant.*
- Email timestamps (9-10 Oct 2026) and the ticket creation time (10 Oct 2026) are later than the stated case date of 14 Sep 2026. Block log RC-2004 is dated 14 Sep, and the block email refers to a 'September' mark. — *Treated the emails as just received. The discrepancy does not change the actions: the leak is within 90 days of the 30 Aug repair under either date. Flagged in the ticket and handover.*
- Tenant says the leak was under the Flat 7 kitchen units. Block management say the Flat 6 ceiling is still wet the next morning; the source is unconfirmed (possibly the machine; Flat 7 also has repeated sealant renewals). — *Unresolved. The engineer was asked to confirm the source; a plumber leak-trace was recommended if the machine is not the cause. Escalated to the PM.*

## Information gaps
- Whether water is still escaping (e.g. supply hose or valve): the tenant was advised to isolate the machine's water valve, and the simulated call reported no new hazards. No specific confirmation that the valve was closed.
- Source of the Flat 6 ingress is unconfirmed; the engineer is asked to investigate on 12 Oct.
- Callback/warranty terms for JOB-8798 and manufacturer warranty status are unknown; the contractor is asked to confirm.
- A firm replacement price is unknown; £350 is the engineer's August estimate. An itemised quote was requested.
- Pets and the tenant's preferred access were not specifically captured (call summary was generic). Concierge access with more than 24h notice was used, and the tenant was asked to tell the provider about pets.
- Landlord's decision on replacement is pending.

## Assumptions
- The leak is contained because the machine is switched off and the tenant reported no new hazards, so the band is urgent rather than emergency.
- The Monday 12 Oct slot with concierge access satisfies the 24h notice rule (booked 10 Oct).
- The callback visit should be low or no cost because it follows the contractor's own temporary fix within 90 days.
- The manufacturer's warranty has probably expired given the machine's age (about 2.5 years); to be confirmed by the contractor.
- Wharf Lane Block Management was messaged using recipient_type 'property_manager' as the closest available type (they are the block managing agent, not our internal PM).

## Communication
- Tenant: Grace was emailed and texted: ApplianceFix South West, Mon 12 Oct 2026 09:00-11:00, via concierge, contact +44 117 000 0110. She was told to keep the machine unplugged, turn off its water isolation valve, dry the floor, switch off at the consumer unit only if safe if water nears sockets, and report any new water. She was told replacement has been requested from the landlord but cannot be promised, asked to mention pets to the provider, and told the machine is recorded as a Beko.
- Landlord: Owen Pryce was emailed: the repair callback is booked within the £250 limit; the machine is about 2.5 years old, not one; it has had 4 faults and £365 spent in 12 months; the engineer said beyond economical repair on 30 Aug (meeting his own standing instruction); and the Flat 6 ingress may involve an insurer. He was asked to confirm in writing whether he approves a replacement at about £350 (approval APR-9BAE23; firm quote to follow) or wants another repair under £250.

## Risk flags
- Water ingress into a third-party flat (Flat 6); block management may raise it with the freeholder's insurer (possible insurance claim or liability).
- Recurring fault: 4th washing machine fault in 12 months, and the leak recurred within 90 days of a temporary fix; replacement assessment recommended.
- Landlord instruction (repair only) conflicts with the engineer's beyond-economical-repair finding; further temporary repairs risk repeat leaks and more damage.
- Water pooled under kitchen units near appliances and sockets; tenant advised on electrical safety.
- Data quality: email dates are later than the stated case date.

## Next steps
- 12 Oct: confirm ApplianceFix SW attended; get the leak-source finding, photos, BER report, itemised replacement quote and callback/warranty position.
- 13 Oct: chase Owen Pryce for written replacement approval if no reply (APR-9BAE23); after about 3 days of silence, escalate to a manager.
- On approval: instruct the replacement (supply, fit, remove old unit) and give the tenant 24h notice.
- Send the engineer's findings and photos to Wharf Lane Block Management re Flat 6 (RC-2004).
- If the machine is not the source of the Flat 6 ingress, book a plumber leak-trace.
- PM to handle the Flat 6 damage and insurance contact (ESC-124DEF).
- Completion check: contractor confirms, tenant confirms, invoice checked against the quote; then close as completed or completed without payment if warranty/callback.
