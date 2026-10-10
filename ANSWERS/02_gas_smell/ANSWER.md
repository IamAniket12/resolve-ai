# Case 02_gas_smell — Answer

**Case status now:** escalated — Gas emergency: tenant told to evacuate and call 0800 111 999. GasSure booked today 13-15 (BKG-62AE07, est £140). CP12 expired. Landlord objects to gas spend. Sent to PM (ESC-7485B8). Check the outcome with contractor and tenant by 16:00 today.  
**Decision:** `escalated`  
**Urgency:** `emergency`  
**Issue category:** gas  
**Confidence:** 0.85  
**Processing status:** completed

## Summary
At 08:15 on Fri 10 Oct 2026, tenant Tom Reilly phoned to report a strong smell of gas in the kitchen near the cooker at 9 Birch Close, Croydon CR0 7EX (PROP-0077, active rolling tenancy TEN-5002). His wife has a headache, which could mean gas or CO exposure. The gas safety certificate (CP12) expired on 30/09/2026. The landlord, Marcus Oyelaran (LL-0220), is abroad until 20 Oct, wants email only, has a £150 spend limit, and has said he does not want to pay for gas work.

## Outcome
The tenant was given gas emergency safety advice by call and SMS: evacuate and call 0800 111 999. A Gas Safe engineer, GasSure London, is booked for a make-safe visit today 10/10/2026 13:00-15:00 (BKG-62AE07, estimated £140, within the £150 limit). The case has been escalated to the property manager as critical (ESC-7485B8) because of the gas safety rule, the expired CP12 and the landlord's objection to paying for gas work.

## Actions taken
- Looked up property PROP-0077, tenancy and repair history. All records agree with the case file: tenancy TEN-5002 is active and rolling, CP12 expired 2026-09-30, landlord spend limit is £150.
- Created emergency maintenance ticket TKT-8A472B (category gas).
- Searched the panel for emergency gas engineers covering CR0 and found CON-TH01 Thames Heating and CON-GS02 GasSure London, both Gas Safe registered.
- Phoned tenant Tom Reilly (+44 7700 900502) with safety advice: evacuate, call 0800 111 999, no switches or flames, turn off at the meter if safe, NHS 111/999 if symptoms get worse, no charge to the tenant. The call ran in simulated mode.
- Sent the same gas emergency advice to the tenant by SMS (MSG-AE97C8, delivered).
- Checked GasSure London (CON-GS02) emergency availability and got same-day slots.
- Booked GasSure London slot SLOT-EME-1, 10/10/2026 13:00-15:00 (booking BKG-62AE07, confirmed, estimated £140). Scope is make-safe plus CO check, with a separate quote for the CP12.
- Sent the tenant the appointment details by SMS (MSG-E7C3F6, delivered).
- Emailed GasSure London the job details (MSG-EEFC1F, delivered).
- Emailed the landlord about the emergency, the booking and cost, the expired CP12 and his statutory duty (MSG-4DF9BB, delivered).
- Escalated to the property manager as critical (ESC-7485B8).
- Set the case status to escalated (STS-E23384) and recorded an internal note (NOTE-C25CC1).

## Failed actions and recovery
- The availability check for Thames Heating Ltd (CON-TH01) failed with HTTP 504 (gateway timeout). I did not retry and went to the next Gas Safe contractor, GasSure London (CON-GS02), who had a same-day emergency slot and was booked.
- The tenant voice call completed, but only in simulated mode with a generic summary. It did not confirm that the tenant called 0800 111 999, that the property is evacuated, or how the occupant is. I sent an SMS as backup and gave these checks to the property manager.

## Escalation
- Required: **yes**
- To: property_manager
- Reason: This is a gas emergency under the hard safety rule, with a possible CO symptom (headache). The gas safety certificate (CP12) has expired, which is a statutory compliance breach. The landlord objects to paying for statutory gas work and is abroad, email only.

### Handover for the human
PROPERTY: PROP-0077, 9 Birch Close, Croydon CR0 7EX. TENANCY: TEN-5002, active and rolling. Tenants are Tom Reilly (+44 7700 900502, tom.reilly@example.com) and Sadie Reilly (+44 7700 900503). Usual access is after 5pm or on Saturdays. REPORT: Tom called at 08:15 on Fri 10/10/2026. He reported a strong gas smell in the kitchen near the cooker that you notice as soon as you walk in, and said his wife has a headache. He had opened the back door. He says the fault is not tenant-caused. COMPLIANCE: The CP12 expired on 2026-09-30 (last check JOB-8700 by GasSure CON-GS02 on 2025-09-28). The boiler is a Baxi 830 from 2014. LANDLORD: Marcus Oyelaran (LL-0220, m.oyelaran@example.com). He is abroad until 20 Oct and wants email only, with a £150 written-approval limit. The CRM note from 2025-11-03 records that he asked not to be billed for gas work, with no agreement reached. DONE: Emergency ticket TKT-8A472B. Safety advice given by call (simulated) and by SMS. GasSure London (Gas Safe 598877) booked today 13:00-15:00, ref BKG-62AE07, estimated £140, scope limited to make-safe and a CO check, with a separate quote for the CP12. The tenant has been texted the appointment details, the contractor has been emailed, and the landlord has been emailed about the emergency, the cost and his statutory duty. Thames Heating's scheduling system returned a 504 error. NEEDS A HUMAN: (1) Phone Tom now to confirm 0800 111 999 has been called, everyone is out and safe, and whether Sadie needs medical advice. (2) Make sure the 13:00 visit happens. By 16:00, get the engineer's findings, any warning notice or capping of the supply, and an invoice of £140 or less. (3) Arrange the CP12 renewal now. It is a legal requirement and the landlord cannot opt out. (4) Any repair quote above £150 needs the landlord's written approval by email. If he refuses statutory gas work, refer to compliance rather than leave the property unsafe. RECOMMENDATION: Go ahead with the make-safe and the CP12 renewal regardless of the landlord's objection, and put his statutory duty to him in writing.

## Conflicts in the information
- The landlord's position (CRM note 2025-11-03, and the tenant's account of what the landlord said last year) is that he will not pay for any gas work. Gas safety repairs and the annual CP12 are statutory landlord obligations. — *Followed the statutory duty and policy (sections 3, 4 and 9): the make-safe was not refused or delayed. The booking is within his £150 limit, he has been informed by email, and the disagreement over future spend is unresolved and escalated to the property manager.*
- The landlord's spend limit of £150 is lower than the policy's £500 emergency make-safe allowance. — *Applied the stricter landlord limit as the policy requires. The booking is estimated at £140, and the contractor was told not to go beyond make-safe or £150 without approval.*

## Information gaps
- It is unknown whether the tenant has called the National Gas Emergency Service (0800 111 999) or whether they have attended. The simulated call did not confirm this, so it has been handed to the property manager to confirm by phone.
- It is unknown whether the property has been evacuated, who is inside, and whether there are pets. The tenant was asked by SMS to tell the engineer about pets.
- The occupant's health (headache, possible CO exposure) is unknown. Medical advice (NHS 111/999) was given and a follow-up is in the handover.
- The source of the gas (cooker, supply pipe or other appliance) is unknown until the engineer attends.
- Access for the 13:00 visit is not confirmed by the tenant. The tenants usually work, and the contractor has been told to phone the tenant first.
- The final repair cost is unknown. Only the £140 call-out estimate is known.

## Assumptions
- The case material is current: the call was on Fri 10 Oct 2026 at 08:15.
- A Gas Safe follow-up visit is needed after the emergency service makes the supply safe, and booking it within the landlord's £150 limit is allowed as emergency make-safe.
- The tenant's wife referred to in the call is co-tenant Sadie Reilly.
- The fault is not tenant-caused, so it is the landlord's responsibility.

## Communication
- Tenant: Called Tom (simulated) and sent an SMS with gas emergency advice: evacuate, leave doors and windows open, call 0800 111 999, no switches or flames, turn off at the meter if safe, NHS 111/999 if symptoms get worse, no gas appliances until cleared, and no charge to the tenant. A second SMS confirmed that a Gas Safe engineer from GasSure London will attend today between 13:00 and 15:00 (ref BKG-62AE07). It said they will phone first, gave their number 020 7946 0102, and asked the tenant to mention any pets.
- Landlord: Emailed Marcus Oyelaran. The email quoted the tenant's report and explained that the tenants were told to evacuate and call 0800 111 999. It said GasSure London is booked today 13:00-15:00, with an estimated call-out of £140 (within his £150 limit), scoped to make-safe only, and that any further quote will be sent to him. It also told him the CP12 expired on 30/09/2026 and that gas safety is a statutory duty that cannot be withheld, and that the property manager will contact him about renewal.

## Risk flags
- Gas emergency: strong gas smell near the cooker (hard safety rule).
- Possible CO or gas exposure symptom: an occupant has a headache.
- Statutory compliance breach: the gas safety certificate (CP12) expired on 30/09/2026.
- The landlord has said he will not pay for statutory gas work, which is a risk of the property being left unsafe and of legal non-compliance.
- Landlord is abroad and email-only until 20 Oct, so approvals may be slow.
- Evacuation and the emergency-line call are not confirmed (simulated call).

## Next steps
- Property manager: phone the tenant today to confirm 0800 111 999 was called, the property is evacuated and the occupant's health.
- Completion check by 16:00 today: get GasSure's findings, any warning or disconnection notice, CO test result, evidence of completion and an invoice of £140 or less.
- Get a CP12 renewal quote from GasSure and approve or arrange it promptly. Get the landlord's written approval by email if it is above £150, or escalate to compliance if he refuses.
- If more repair work is needed, send the quote to the landlord for written approval (limit £150). If he refuses a statutory gas repair, escalate to compliance.
- If the supply is capped, check how the tenants will cook and heat the home, and treat restoring supply as an emergency.
- Chase the landlord after about 3 working days if there is no reply on the quote or the CP12.
