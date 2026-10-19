# 5. Compliance: how to make money without getting sued

**This is a practical checklist, not legal advice.** TCPA class actions carry statutory damages commonly cited at
$500-$1,500 *per call or text*, so one sloppy campaign can wipe out a year of profit. Spend an hour with a
telecom/marketing attorney before your first client campaign, and have them review your client agreement.

## Your own outreach (selling to HVAC owners)

**Cold email (CAN-SPAM)**
- Accurate From name and domain; subject lines that match the content (no fake "Re:" on a first touch)
- Your physical postal address in the signature (a virtual mailbox is fine)
- A working opt-out, honored within 10 business days (your sending tool handles this; also run
  `bookedout mark <email> --status do_not_contact` so the engine never exports them again)
- Business addresses only; don't buy consumer lists

**Cold calls**
- Dial manually. No autodialers, no prerecorded voicemail drops, **no AI voice calling for outreach**. Many
  owners list cell phones, and the FCC's February 2024 declaratory ruling treats AI-generated voices as
  "artificial" voices under the TCPA, which require prior consent.
- Check state telemarketing rules for the states you call (several, such as Florida, Oklahoma and Maryland,
  have their own laws with calling-hour limits and registration requirements). Call business hours only.
- Honor "don't call me" immediately: `bookedout call <lead> --outcome do_not_call`.

**Cold texts:** don't. Texting a cell number you scraped is the fastest way into a TCPA lawsuit.

**The after-hours audit:** calling a company's advertised business line and noting whether anyone answers is
fine. Don't pretend to be a homeowner, don't book fake appointments, and don't record without consent.

## Client campaigns (contacting *their* customers)

**Email to past customers and quote recipients:** fine with an opt-out and the client's identity and address.

**Texts (SMS):**
- Marketing texts need **prior express written consent** from the customer. Ask the client how consent was
  collected (service agreement checkbox, booking form, opted in by text). No consent → no marketing texts.
- Every client's texting number must be **A2P 10DLC registered** under the client's brand before sending.
  Registration needs their legal name, EIN, website with a privacy policy that says mobile numbers aren't shared
  or sold, and a description of how customers opt in. Allow several business days for approval.
- Every text: identify the business, include "Reply STOP to opt out", honor STOP instantly.
- Send 9am-8pm in the recipient's time zone (some states are stricter than federal rules).
- The client warrants consent in writing (put it in your agreement), and you keep a suppression list per client.

**Phone follow-up on unsold estimates:** manual calls by the client's team or your callers. The established
business relationship exemption from Do Not Call lists generally runs 3 months after an inquiry and 18 months
after a purchase. For older quotes on numbers registered with DNC, only call with consent. Never use AI voice or
prerecorded calls for these outbound campaigns without prior express written consent.

**Missed-call text-back:** keep it informational ("Sorry we missed your call, what can we help with?"), no
promotion, include opt-out, send once. Have counsel confirm your template.

## The AI Dispatcher (inbound calls)

- **Disclose that it's AI** at the start of every call ("I'm the virtual assistant for..."). Some states require
  bot disclosure, and it builds trust anyway.
- **Call recording:** several states require all-party consent (including California, Florida, Illinois,
  Maryland, Massachusetts, Montana, New Hampshire, Pennsylvania and Washington). Put "this call may be recorded"
  in the greeting, for every client, everywhere.
- **Safety:** gas smell or carbon monoxide alarm → tell the caller to leave the building and call 911 or the gas
  utility from outside, then alert on-call. That's in the prompt; test it on every build.
- **No pricing promises** beyond fees the client has approved in writing (diagnostic fee, trip charge).
- Human transfer available on request, always.

## Contracts and data

- Written agreement for every client: scope, fees, term, guarantee terms, the client's consent warranty for
  their customer data, data deletion on termination, limitation of liability.
- Store client customer lists only in the client's sub-account, never in spreadsheets you email around.
- Lead databases (`*.db`) and exports contain personal data and are git-ignored. Keep it that way.

## Website (needed for A2P registration and trust)

`website/privacy.html` and `website/terms.html` include SMS language carriers look for. Replace the placeholders
(legal name, address, email) before you publish, and mirror the same language on each client's website if you
register texting under their brand.
