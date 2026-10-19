# Client onboarding

## The moment they pay

- [ ] `bookedout mark <lead> --status won`
- [ ] Welcome email (`sales/follow-up.md`) with the onboarding form link
- [ ] Agreement sent for e-signature (scope, fees, guarantee terms, consent warranty, data handling)
- [ ] Kickoff call booked within 48 hours
- [ ] Client sub-account created from your snapshot

## Onboarding form (10 minutes for the owner; build it in your CRM or Google Forms)

**Business**
1. Legal business name, DBA, EIN (for A2P texting registration), business address, website
2. Owner name, cell, email; office manager name, email
3. Service area (cities / ZIPs), business hours, holidays closed
4. Services offered and not offered; brands; dealer status
5. Field service software (ServiceTitan / Housecall Pro / Jobber / FieldEdge / other) and who has admin access

**Phones**
6. Main line number and carrier / phone system (RingCentral, Nextiva, Weave, carrier, cell...)
7. Who answers during the day? How many lines/CSRs?
8. What happens after hours today (voicemail, answering service, on-call cell)?
9. On-call schedule: who, which number, rotation
10. What counts as an emergency for you? (default: no heat below 32°F, vulnerable occupants, gas/CO = safety)

**Money**
11. Diagnostic fee, after-hours fee, membership plan details, financing partner
12. Average repair ticket, average replacement ticket, replacement close rate (rough is fine)

**Booking**
13. Job types and durations, arrival windows, how many repair slots per day, estimate calendar owner
14. Anything the dispatcher must never book or promise

**Estimates (for the sprint)**
15. Approximate number of unsold quotes in the last 24 months
16. How was SMS consent collected (agreement checkbox, booking form, none)?
17. Who runs recovered appointments, and how fast can they go out?
18. The reason-to-act-now offer you're willing to honor

## Kickoff call agenda (30 minutes)

1. Goals and what success looks like at day 14 / day 60 (write the numbers down)
2. Walk the estimate export together (sprint) or the call flow (dispatcher)
3. Confirm emergency rules, fees, booking rules, transfer numbers
4. Pick the dispatcher voice together (play 3)
5. Agree the daily/weekly update channel and response times
6. Next steps with dates

## AI Dispatcher go-live (5 business days)

| Day | Task |
|---|---|
| 1 | Clone the demo agent; fill variables; connect calendar/FSM booking; build post-call automations |
| 1 | Start A2P 10DLC registration for confirmations and missed-call text-back |
| 2 | Run the 20-scenario test script (`delivery/ai-dispatcher-prompt.md`); fix and retest |
| 3 | Owner/office manager calls it 5 times; adjust tone and rules |
| 4 | Set call forwarding: after-hours + no-answer/busy → AI number. Test from a cell phone |
| 4 | Brief the team: what a transfer sounds like, where summaries land, how to flag a bad call |
| 5 | Live. Watch every call for 48 hours; send the owner a summary of night one |

Week 1-4: review 10 recordings/week, tune the prompt, send the weekly report every Monday.
Day 60: guarantee check + Complete tier conversation + annual prepay offer.

## Offboarding (if they cancel)

Export their data to them, delete it from your systems within 30 days, release the number or port it to them,
remove forwarding, and ask for honest feedback. Leave the door open; many come back in the next cold season.
