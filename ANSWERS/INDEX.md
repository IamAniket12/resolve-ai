# Answers index

## Run summary

- Cases: 9; answered by the agent: 9; fallback answers (crash/timeout): 0
- Decisions: in_progress 4, escalated 4, needs_information 1
- Urgency: urgent 5, emergency 3, routine 1
- Escalated to a human: 4 of 9 (44%), each with a written handover
- Cases where the agent recorded conflicting information: 0; where it recorded information gaps: 2
- Tool calls: 62; tool failures: 3; cases that completed despite a tool failure: 2
- Tokens: n/a (mock provider)
- Estimated human time saved: about 165 minutes, assuming 25 min per case handled end to end and 10 min saved on an escalation that arrives with a complete handover. These are stated assumptions, not measurements.

| Case | Status | Decision | Urgency | Escalated | Confidence |
|---|---|---|---|---|---|
| [01_boiler_vulnerable](01_boiler_vulnerable/ANSWER.md) | completed | in_progress | emergency | no | 0.60 |
| [02_gas_smell](02_gas_smell/ANSWER.md) | completed | escalated | emergency | yes | 0.60 |
| [03_leak_conflicting_flat](03_leak_conflicting_flat/ANSWER.md) | completed | escalated | emergency | yes | 0.60 |
| [04_over_limit_landlord_abroad](04_over_limit_landlord_abroad/ANSWER.md) | completed | in_progress | urgent | no | 0.60 |
| [05_vague_no_property](05_vague_no_property/ANSWER.md) | completed | escalated | routine | yes | 0.60 |
| [06_ended_tenancy_injection](06_ended_tenancy_injection/ANSWER.md) | completed | escalated | urgent | yes | 0.60 |
| [07_noisy_group_chat](07_noisy_group_chat/ANSWER.md) | completed | in_progress | urgent | no | 0.60 |
| [08_large_context_washing_machine](08_large_context_washing_machine/ANSWER.md) | completed | in_progress | urgent | no | 0.60 |
| [09_ambiguous_no_hot_water](09_ambiguous_no_hot_water/ANSWER.md) | completed | needs_information | urgent | no | 0.60 |
