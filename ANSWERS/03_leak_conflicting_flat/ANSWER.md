# Case 03_leak_conflicting_flat — Answer

**Case status now:** appointment booked — Emergency electrician Bright Spark booked today 13:00-15:00 (BKG-B7D4A1). PM escalated to contact Hove Lettings (Flat 2) to stop the leak at source. Check completion report tonight or by 11 Oct 09:00.  
**Decision:** `escalated`  
**Urgency:** `emergency`  
**Issue category:** plumbing/leak with electrical hazard (water through light fitting)  
**Confidence:** 0.85  
**Processing status:** completed

## Summary
Tenant Lena Fischer (TEN-5003, active) emailed at 06:50 on Sat 10 Oct 2026. Since about 05:00, water has been dripping steadily through the bathroom ceiling light fitting at Flat 1, 44 Clifton Street, Brighton BN1 3PJ (PROP-0113, landlord Helen Carter LL-0301). She believes it comes from Flat 2 upstairs, which is managed by a different agent (Hove Lettings). She is at work from 8am and can only be reached by email today. Water through a light fitting is an electrical emergency as well as a leak. The leak source is outside our control. She also says the ceiling was stained at move-in, but the check-in inventory says it was not.

## Outcome
Emergency NICEIC electrician Bright Spark Electrical is booked for today 13:00-15:00 (BKG-B7D4A1, £130 call-out) to make the lighting circuit safe, with access by the office-held key safe. The case is escalated to the property manager to contact Hove Lettings and stop the leak at source in Flat 2, and to give the contractor the key safe code.

## Actions taken
- Looked up property PROP-0113, tenancy and repair history. Records match the case file; tenancy active; no vulnerability; SMS disabled; key safe access.
- Created emergency ticket TKT-96050D (category electrical).
- Searched the approved panel for emergency electricians (found CON-EL05 Bright Spark Electrical, NICEIC) and emergency plumbers (found CON-SP04 Sussex Plumb & Heat) for BN1 3PJ.
- Checked CON-EL05 emergency availability and booked SLOT-EME-1, today 10 Oct 13:00-15:00. Booking BKG-B7D4A1 confirmed, estimated cost £130.
- Emailed the tenant (MSG-CE54B6): booking details, safety advice (isolate at consumer unit, don't use the light, call 999 if it gets worse), key safe access, the pets question, and a request for move-in photos of the ceiling.
- Emailed the landlord (MSG-CD4197): emergency works and spend, the suspected upstairs source, and possible insurance/third-party recovery.
- Emailed the contractor the job brief and scope (MSG-79C8C7).
- Called the contractor to confirm attendance (simulated call). They confirmed the slot and said they would call the tenant 30 minutes before arrival.
- Escalated to the property manager (ESC-3998F1, high).
- Set case status to appointment_booked (STS-F0A545).
- Recorded an internal note (NOTE-319EF0).

## Failed actions and recovery
- None

## Escalation
- Required: **yes**
- To: property_manager
- Reason: The leak source is in Flat 2, which Hove Lettings manages, not us. Only they can stop it, and I have no tool route to contact a third-party agent. The damage may also lead to an insurance or third-party recovery claim.

### Handover for the human
Property: Flat 1, 44 Clifton Street, Brighton BN1 3PJ (PROP-0113), ground-floor flat in a converted house. Landlord Helen Carter, helen.carter@example.com, +44 7700 900301. Tenant Lena Fischer, active tenancy, email only today, SMS disabled. Issue: steady drip through the bathroom ceiling light since ~05:00 on 10 Oct, believed to be from Flat 2 above. Bucket in place; light off at the wall switch only. Done: ticket TKT-96050D (emergency). Bright Spark Electrical (CON-EL05, NICEIC, +44 20 7946 0105) booked today 13:00-15:00, BKG-B7D4A1, £130, within the £500 emergency limit. Contractor confirmation call was simulated, so a real confirmation is still needed. Tenant, landlord and contractor all emailed. Status: appointment_booked. You need to: (1) Phone Hove Lettings on 01273 000000 today to get Flat 2 checked and the water turned off at source. If they can't be reached and the leak worsens, consider a communal stopcock or the emergency plumber Sussex Plumb & Heat (CON-SP04, +44 1273 000222). (2) Give Bright Spark the key safe code by phone when they arrive. They plan to call the tenant first, but she can't be reached today. (3) Tell the landlord/freeholder about a possible insurance or third-party claim. Once the source is fixed, get a quote for the ceiling repair; landlord approval is likely needed as it will probably exceed £250. Conflict: the tenant says the ceiling was stained at move-in, but the 10 Jan 2026 inventory says no staining. Photos have been requested; this matters for liability and the deposit, not today's work. Recommended: contact Hove Lettings now, keep the make-safe booking, and review the electrician's report tonight or by 09:00 on 11 Oct.

## Conflicts in the information
- The tenant says the bathroom ceiling was already stained at move-in. The check-in inventory of 10 Jan 2026 records 'Bathroom ceiling: good condition, no staining.' — *For now the inventory is trusted as the signed record. The tenant has been asked for move-in photos and the conflict is recorded on the ticket. It doesn't change the emergency action; liability and the deposit are left for later.*
- The contractor said they would call the tenant 30 minutes before arrival, but the tenant says she can't be contacted by text or phone today, email only. — *Access is via the key safe, with the code held by the office. The PM has been asked to take the contractor's call and give the code.*

## Information gaps
- We don't know the exact leak source (Flat 2 bathroom, pipework or roof). It's blocked until Hove Lettings or the Flat 2 occupier gives access; escalated to the PM.
- No contact for Hove Lettings other than 01273 000000, and no tool route to them. Escalated.
- Whether the drip is getting worse is unknown, as the tenant is at work. She has been told what to do if it gets worse.
- Pets unknown; the tenant has been asked.
- No move-in photos to support the tenant's staining claim; requested.
- Contractor confirmation came from a simulated call; a real confirmation is still needed.

## Assumptions
- The drip is contained (bucket) and there is no flooding or ceiling collapse, so the 999 rule does not apply. The tenant has been told when to call 999.
- Because this is an emergency, the key safe booking went ahead without the tenant agreeing first. Her records list key safe access and she can't be reached except by email.
- The electrician's make-safe call-out (£130) is within the £500 emergency authority, so it went ahead without landlord approval. The landlord was told the same day.

## Communication
- Tenant: Email (MSG-CE54B6). It said this is being treated as an emergency (TKT-96050D) and that Bright Spark Electrical (+44 20 7946 0105) will attend today 13:00-15:00 via the key safe. It told her not to use the light, to isolate at the consumer unit if safe, to keep the bucket in place, and to call 999 or leave the room if it gets worse or she sees sparks. It said we are contacting the upstairs agent, asked about pets, explained that the inventory shows no staining, and asked for any move-in photos.
- Landlord: Email to Helen Carter (MSG-CD4197): the tenant's report quoted word for word, the emergency electrician booked today 13:00-15:00 at £130 within emergency authority, the source is suspected to be Flat 2 (Hove Lettings), a ceiling repair estimate will follow once the source is fixed, and she may wish to tell her insurer or the freeholder.

## Risk flags
- Water coming through a ceiling light fitting: electrical shock and fire risk.
- The leak source is in a third-party-managed flat outside our control, so the leak may continue and damage the property.
- Possible insurance or third-party recovery claim.
- The tenant can't be reached by phone today, so access relies on the office-held key safe.
- Conflict between the tenant's account and the inventory on existing staining, with deposit and liability implications.

## Next steps
- PM to call Hove Lettings (01273 000000) today to stop the leak at source in Flat 2.
- PM to give Bright Spark the key safe code when they call on arrival.
- Confirm attendance and get the electrician's completion report and photos by tonight or 11 Oct 09:00. Check the invoice against the £130 estimate.
- Email the tenant and landlord with the electrician's findings.
- Once the source is confirmed fixed, get a quote for the ceiling and light repair and send the landlord a quote-approval email if it exceeds £250.
- Settle who is liable for the staining once the tenant's photos arrive or a new inspection is done. Consider recovery from the Flat 2 owner or the buildings insurance.
- Chase Hove Lettings and the landlord after 3 days if there's no reply.
