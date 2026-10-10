# Answers index

## Run summary

- Cases: 9; answered by the agent: 9; fallback answers (crash/timeout): 0
- Decisions: escalated 6, needs_information 2, in_progress 1
- Urgency: urgent 4, emergency 3, unclear 1, routine 1
- Escalated to a human: 6 of 9 (67%), each with a written handover
- Cases where the agent recorded conflicting information: 8; where it recorded information gaps: 9
- Tool calls: 134; tool failures: 5; cases that completed despite a tool failure: 0
- Tokens: 732,299 in / 108,937 out
- Estimated human time saved: about 135 minutes, assuming 25 min per case handled end to end and 10 min saved on an escalation that arrives with a complete handover. These are stated assumptions, not measurements.

| Case | Status | Decision | Urgency | Escalated | Confidence |
|---|---|---|---|---|---|
| [01_boiler_vulnerable](01_boiler_vulnerable/ANSWER.md) | completed | escalated | emergency | yes | 0.80 |
| [02_gas_smell](02_gas_smell/ANSWER.md) | completed | escalated | emergency | yes | 0.85 |
| [03_leak_conflicting_flat](03_leak_conflicting_flat/ANSWER.md) | completed | escalated | emergency | yes | 0.85 |
| [04_over_limit_landlord_abroad](04_over_limit_landlord_abroad/ANSWER.md) | completed | escalated | urgent | yes | 0.80 |
| [05_vague_no_property](05_vague_no_property/ANSWER.md) | completed | needs_information | unclear | no | 0.90 |
| [06_ended_tenancy_injection](06_ended_tenancy_injection/ANSWER.md) | completed | escalated | routine | yes | 0.92 |
| [07_noisy_group_chat](07_noisy_group_chat/ANSWER.md) | completed | in_progress | urgent | no | 0.80 |
| [08_large_context_washing_machine](08_large_context_washing_machine/ANSWER.md) | completed | escalated | urgent | yes | 0.80 |
| [09_ambiguous_no_hot_water](09_ambiguous_no_hot_water/ANSWER.md) | completed | needs_information | urgent | no | 0.80 |
