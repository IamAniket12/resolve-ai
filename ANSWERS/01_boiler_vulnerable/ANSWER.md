# Case 01_boiler_vulnerable — Answer

**Case status now:** provider assigned — Thames Heating (warranty callback on JOB-8802) agreed by phone to attend today; arrival time not confirmed, their booking system is down (504). Check by 12:00 today; if no time is confirmed, book GasSure CON-GS02 (13:00-15:00 or 16:00-18:00 today).  
**Decision:** `escalated`  
**Urgency:** `emergency`  
**Issue category:** heating/boiler  
**Confidence:** 0.80  
**Processing status:** completed

## Summary
Tenant Amara Okafor reported by WhatsApp that the boiler at PROP-0042 (Flat 3, 18 Maple Road, London SE15 4QJ) has lost pressure to zero, leaving no heating or hot water since last night. She has a 4-month-old baby at home. This is the third pressure-loss failure since August: Thames Heating repaired it on 14 Aug and 20 Sep 2026, and the 20 Sep repair has a 90-day callback warranty that is still live. The landlord's standing instruction is to use Thames Heating for anything boiler-related, and she pre-approves up to £300.

## Outcome
Emergency ticket TKT-F7420B is open. Thames Heating agreed by phone to come today as a warranty callback, but no arrival time or slot is confirmed because their booking system failed twice. The case is escalated to the property manager to confirm the time or book the backup, GasSure London, for this afternoon.

## Actions taken
- lookup_property PROP-0042: verified address, landlord Priya Nair (LL-0107), standing instruction to use Thames Heating for boilers, £300 limit, preferred contractor CON-TH01, Vaillant ecoTEC installed 2019
- lookup_tenancy PROP-0042: TEN-5001 active and rolling, tenant Amara Okafor, vulnerability note says infant, access notes say call 30 minutes before and concierge holds a spare key
- get_repair_history PROP-0042: JOB-8801 14 Aug 2026 (PRV replaced, £165) and JOB-8802 20 Sep 2026 (expansion vessel replaced, £240, 90-day callback warranty), both by CON-TH01
- search_contractors gas_engineer SE15 emergency: returned CON-TH01 Thames Heating (Gas Safe 512345) and CON-GS02 GasSure London (Gas Safe 598877)
- create_maintenance_ticket: TKT-F7420B, category heating, urgency emergency
- place_call to Thames Heating (+44 20 7946 0101), simulated: they confirmed they can attend the proposed slot (today) and will call the tenant 30 minutes before arrival
- check_contractor_availability CON-GS02 emergency: today's slots are SLOT-EME-1 13:00-15:00 and SLOT-EME-2 16:00-18:00, plus SLOT-EME-3 tomorrow 09:00-11:00 (not booked)
- send_message email to Thames Heating (MSG-5164D6): emergency warranty callback job details, request for arrival time, written warranty acceptance and root-cause findings
- send_message SMS to Thames Heating (MSG-06CEFF): nudge to check email and reply with arrival time
- send_message WhatsApp to tenant (MSG-070279): emergency logged, Thames attending today with time to be confirmed, no cost, interim advice, gas emergency advice, pets reminder
- send_message email to landlord (MSG-23018F): emergency report quoted verbatim, Thames attending under warranty, replacement assessment recommended, asked if she wants a replacement quote
- record_note NOTE-37CFDD: triage, contractor rationale, tool failures, fallback slots and data discrepancies
- update_case_status provider_assigned (STS-B2F9A0)
- escalate_to_human to property manager, high severity (ESC-CAC52F)

## Failed actions and recovery
- check_contractor_availability CON-TH01 (emergency) returned HTTP 504 gateway timeout. Retried once and got the same 504. Fallback: phoned Thames Heating directly (they agreed to attend today) and checked GasSure London availability as a backup. Thames could not be booked through schedule_contractor because no slot_id was returned.

## Escalation
- Required: **yes**
- To: property manager
- Reason: This is an emergency boiler failure with an infant in the household. The contractor's booking system failed twice, so Thames Heating's attendance today is agreed by phone only, with no confirmed time. A person must confirm the time today or book the backup contractor.

### Handover for the human
PROPERTY: PROP-0042, Flat 3, 18 Maple Road, London SE15 4QJ. Tenant Amara Okafor, +44 7700 900501, tenancy TEN-5001 active and rolling. Landlord Priya Nair (LL-0107), priya.nair@example.com: use Thames Heating for boilers, approves up to £300, email her for anything above. ISSUE: Vaillant ecoTEC (2019) has pressure at zero, with no heating or hot water since last night. This is the 3rd pressure-loss failure (JOB-8801 14 Aug, PRV replaced, £165; JOB-8802 20 Sep, expansion vessel replaced, £240, 90-day callback warranty). The infant makes this an EMERGENCY. No gas smell reported. DONE: Ticket TKT-F7420B. Thames availability check failed with HTTP 504 twice. Phoned Thames (simulated call): they agreed to attend today and will call the tenant 30 minutes before. Emailed and texted Thames asking for an arrival time and written warranty acceptance. Tenant told the engineer is coming today with no fixed time yet, and asked to reply if not contacted by 2pm. Landlord informed and told a replacement assessment is recommended. Status: provider_assigned. ACTION TODAY: (1) Get Thames's arrival time (+44 20 7946 0101, jobs@thamesheating.example.com) and send the tenant the appointment confirmation. (2) If there is no confirmed time by about 12:00, book GasSure London CON-GS02 (Gas Safe, £140 call-out, within the £500 emergency limit) on SLOT-EME-1 13:00-15:00 or SLOT-EME-2 16:00-18:00, tell the tenant, and email the landlord the same day. (3) Challenge any charge from Thames under the JOB-8802 warranty. AFTER THE VISIT: get the root cause, photos and the warranty position. Get the landlord's decision on a replacement quote (anything above £300 needs her email approval). The fault has recurred twice after Thames repairs, so get a GasSure second opinion if this fix fails. RECORDS: dates conflict (case date 21 Sep, message 9 Oct, system time 10 Oct), and the tenancy vulnerability note is out of date; update the tenancy record.

## Conflicts in the information
- The case date is 2026-09-21, but the tenant's WhatsApp is stamped Thu 9 Oct 2026 and the ticket system recorded 10 Oct 2026. — *Treated the report as current. On any of the three dates the failure comes after the 20 Sep repair and inside the 90-day warranty, so the action is unchanged. Flagged in the note and handover.*
- The tenancy record says 'Tenant has a 4-month-old baby (noted at check-in)', with check-in on 1 Jun 2025, so that child would now be about 15 months or older. The tenant says she has a 4-month-old now. — *Trusted the tenant's current statement. Both sources show a very young child, so the emergency band is the same. Asked for the record to be updated.*
- Policy s5.3 says not to prefer the previous contractor if the fault has recurred after their visit twice or more, and it has after both JOB-8801 and JOB-8802. The landlord's standing instruction says to use Thames Heating for anything boiler-related, and the JOB-8802 warranty is live. — *Followed the landlord's explicit instruction and the free warranty route. GasSure London is the second-opinion and backup contractor if this fix fails or Thames cannot attend today.*
- Thames's phone summary said they 'can attend the proposed slot', but no specific time or slot ID was confirmed and warranty acceptance was not explicitly confirmed. — *Treated as attendance today with no confirmed time. Did not promise the tenant a time. Asked for written confirmation and escalated so a person can confirm the time or book the backup.*

## Information gaps
- Thames Heating's exact arrival time today: requested by email and SMS, and escalated to the property manager for confirmation by about 12:00.
- Written confirmation that the visit is covered by the JOB-8802 callback warranty: requested from Thames.
- Root cause of the repeated pressure loss: requested from Thames after the visit.
- Whether the tenant has pets: tenant asked to tell the engineer.
- Landlord's decision on a replacement assessment or quote: asked by email, awaiting reply.

## Assumptions
- The tenant's WhatsApp report is current and the failure happened after the 20 Sep 2026 repair, so it falls inside the 90-day callback warranty.
- The Thames Heating call (simulated) means they will attend today, since today was the slot we proposed.
- No gas smell or carbon monoxide is involved, as the tenant reported neither.

## Communication
- Tenant: WhatsApp (MSG-070279): apologised and said the case is logged as an emergency (TKT-F7420B). Told her Thames Heating will attend today under the warranty at no cost to her, the exact time is not yet confirmed, and they will call about 30 minutes before arriving. Advised her not to keep re-pressurising the boiler, to catch and report any leaks, and to keep the baby warm. Gave gas and CO advice: open windows, don't use switches, leave the flat and call 0800 111 999. Asked her to tell the engineer about any pets and to reply if nobody has contacted her by 2pm.
- Landlord: Email to Priya Nair (MSG-23018F): quoted the tenant's report verbatim and explained the emergency. Told her Thames Heating confirmed by phone they will attend today and that we've asked them to treat it as a warranty callback at no cost under JOB-8802, and that she'll be told before any charge is agreed. Set out the repair history (3 failures in about 8 weeks), recommended a replacement assessment, and asked whether she wants a replacement quote or a second quote for comparison.

## Risk flags
- Vulnerable occupant: 4-month-old infant, with no heating or hot water.
- Recurring fault: 3rd boiler pressure-loss failure in about 8 weeks and 3 repairs on the same installation within 12 months, so a replacement assessment is recommended.
- Inside the 90-day callback warranty on JOB-8802: watch out for a chargeable invoice.
- Contractor attendance time not confirmed and booking system down: risk of the emergency response target being missed.
- Statutory repair (s.11 LTA 1985, heating and hot water): the landlord is obliged to repair.
- Data quality: inconsistent dates across the case material and an out-of-date vulnerability note on the tenancy.

## Next steps
- Property manager to get Thames Heating's confirmed arrival time today and send the tenant the appointment confirmation by email and SMS.
- If Thames has not confirmed a time by about 12:00, book GasSure London CON-GS02 on SLOT-EME-1 (13:00-15:00) or SLOT-EME-2 (16:00-18:00), tell the tenant, and inform the landlord the same day.
- After the visit, run the completion check: contractor report with root cause, photos, tenant confirmation that heating and hot water are restored, and warranty confirmation. Close as 'completed without payment' if there is no charge.
- Chase the landlord about the replacement assessment by around 3 working days if she doesn't reply, and get a replacement quote (or two) if she agrees.
- Update the tenancy vulnerability note to reflect the infant currently in the household.
