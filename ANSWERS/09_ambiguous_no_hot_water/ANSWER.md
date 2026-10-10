# Case 09_ambiguous_no_hot_water — Answer

**Case status now:** awaiting tenant — Waiting for Tenant: self-check results (shower isolator/MCB, kitchen hot tap) + choice of Bright Spark slot Mon 12 Oct 9-11 or 2-4. Check today 16:00; if no reply, book SLOT-URG-1 on 11 Oct to stay inside the 3-working-day target.  
**Decision:** `needs_information`  
**Urgency:** `urgent`  
**Issue category:** electrical (electric shower) / possible heating/boiler hot water  
**Confidence:** 0.80  
**Processing status:** completed

## Summary
Tenant Mo Hussain reported through the tenant portal at 07:55 on 10 Oct 2026 that the shower at 5 Stanley Terrace, Nottingham NG7 1AB (PROP-0233) was running cold. He called it 'no hot water', but the heating came on at 06:00 and he hadn't checked the kitchen tap. The property and CRM records both say the shower is a Triton electric shower on its own circuit and the combi boiler feeds the taps only, so this is most likely an electric shower fault, not a boiler fault. The only open question is whether the hot taps work. If they don't, there is a separate boiler fault.

## Outcome
Ticket TKT-9F31F9 is open as urgent and on hold waiting for the tenant. He has been asked to do safe self-checks and say whether the kitchen hot tap works, and to choose between two Bright Spark Electrical slots on Mon 12 Oct (09:00-11:00 or 14:00-16:00). The landlord has been told about the job, which is within his £250 authority. Nothing is booked yet.

## Actions taken
- lookup_property PROP-0233: confirmed address, landlord Graham Steele (LL-0702), standard authority, £250 limit, no preferred contractors, Triton electric shower on its own circuit, combi boiler feeds taps only, gas certificate valid to 2027-04-10, electrical safety report (EICR) valid to 2028-05-20
- lookup_tenancy PROP-0233: TEN-5013 active, tenant Mo Hussain, no vulnerability notes, access note 'Shift worker; prefers text. Available mornings before 11.'
- get_repair_history PROP-0233: one job only, JOB-8755 boiler service 2026-06-02 by Trent Plumb & Heat (CON-TP12), no faults, £80
- search_contractors electrician NG7 1AB: Bright Spark Electrical CON-EL05 (NICEIC 77001, rating 4.7, call-out £130)
- search_contractors gas_engineer NG7 1AB: Trent Plumb & Heat CON-TP12 covers NG (Gas Safe 644210); Thames Heating CON-TH01 does not cover NG
- create_maintenance_ticket: TKT-9F31F9, category electrical, urgency urgent
- check_contractor_availability CON-EL05 urgent: SLOT-URG-1 Mon 12 Oct 09:00-11:00, SLOT-URG-2 Mon 12 Oct 14:00-16:00, SLOT-URG-3 (same times as SLOT-URG-1)
- send_message SMS to tenant +44 7700 900631 (MSG-852257, delivered): explained the shower is electric; asked for checks (pull-cord isolator, fuse box shower switch/RCD reset once only, temperature dial, kitchen hot tap); safety advice on burning smell or sparking; offered both Monday slots; warned an avoidable call-out may be chargeable; asked about pets
- send_message email to landlord g.steele@example.com (MSG-A1ADE8, delivered): tenant's words quoted, diagnosis, planned Bright Spark visit (£130 call-out within £250 authority), quote to come if the repair costs more than £250, Trent Plumb & Heat proposed if the taps are also cold, option to use his own contractor
- record_note on TKT-9F31F9 (NOTE-36D3C9): triage reasoning, slot details, conflicting access times
- update_case_status TKT-9F31F9 -> awaiting_tenant (STS-9001F3) with check at 16:00 today

## Failed actions and recovery
- None

## Escalation
- Required: **no**

## Conflicts in the information
- The tenant calls it 'no hot water' and links the cold shower to the boiler. The property record and CRM both say the shower is an electric Triton on its own circuit that the boiler doesn't feed. — *Trusted the records: the property database and CRM agree, and the heating working at 06:00 points to a running boiler. The job is triaged as an electric shower fault (electrician). Whether the hot taps also fail is still being checked with the tenant.*
- Access times: the tenancy record says 'Available mornings before 11', but today's portal ticket says 'I'm back at 2pm'. — *Not assumed. Both a morning and an afternoon Monday slot were offered and the tenant was asked to choose before booking. The morning slot (matches the record) is the fallback if he doesn't reply.*

## Information gaps
- Whether the kitchen/basin hot taps run hot. This decides whether a Gas Safe engineer is also needed. Asked the tenant by SMS.
- Whether the shower isolator or fuse box switch has tripped (could be fixed without a call-out). Asked the tenant to check safely.
- Which Monday slot the tenant can do. Asked by SMS; booking waits for his reply.
- Pets at the property: unknown. Asked the tenant.
- Exact repair cost if the shower element or the whole unit needs replacing: unknown until the electrician attends. The landlord has been told a quote will follow if it's over £250.

## Assumptions
- The heating working at 06:00 means the boiler is firing, so a boiler fault is less likely.
- The Bright Spark call-out (£130) plus a minor repair will stay within the £250 standard authority, so landlord approval isn't needed to send the electrician.
- SLOT-URG-3 is a duplicate of SLOT-URG-1 (same times).
- No vulnerability, because the tenancy record has no vulnerability notes and the tenant mentioned none.

## Communication
- Tenant: SMS (delivered): the shower is electric and separate from the boiler. Asked him to check the pull-cord isolator, the fuse box shower switch/RCD (reset once only), the temperature dial, and whether the kitchen hot tap runs hot. Told him to switch off at the fuse box and call us if there's any burning smell or sparking. Offered Bright Spark Electrical on Mon 12 Oct, 9-11am or 2-4pm, to be confirmed only after he replies. Asked about pets and warned that an avoidable call-out may be chargeable. He was not promised a same-day visit.
- Landlord: Email (delivered) to Graham Steele: quoted the tenant's report and explained it's likely an electric shower fault, not the boiler. Said the tenant is doing self-checks and that the planned Bright Spark NICEIC electrician visit on Mon 12 Oct costs £130, within his £250 authority. Said a quote for approval will follow if the repair costs more than £250, that Trent Plumb & Heat will be proposed if the taps are also cold, and that he can use his own contractor if he tells us today.

## Risk flags
- Electric shower fault: there's a small chance of an electrical hazard. The tenant has been told to isolate the shower and report any burning smell, scorching, or repeat tripping, which would make this an electrical emergency.
- Loss of the shower for a shift worker: response target is 3 working days (by Wed 14 Oct 2026); the tenant asked for same day.

## Next steps
- Today 16:00: check for the tenant's SMS reply with check results and preferred slot.
- If he chooses a slot: schedule_contractor CON-EL05 with SLOT-URG-1 or SLOT-URG-2 against TKT-9F31F9, then send the appointment confirmation by email and SMS and set status to appointment_booked.
- If the self-checks fix it: confirm with the tenant, close as closed_no_action and tell the landlord.
- If the kitchen hot tap is also cold: raise a heating ticket and book Trent Plumb & Heat (CON-TP12, Gas Safe) within the urgent band; tell the landlord.
- If there's no reply by this evening: book SLOT-URG-1 (Mon 09:00-11:00, matches his recorded availability) and text him, to meet the 3-working-day target (by Wed 14 Oct).
- If the electrician finds the work will cost more than £250 (e.g. replacement shower): get a quote and send it to the landlord for approval before booking the work.
- After the visit: completion check (contractor says done, tenant confirms, invoice no higher than quote), then close.
