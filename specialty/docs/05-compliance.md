# 5. Compliance and ethics

**A practical checklist, not legal advice.** This business is B2B, so the risks are lower than consumer
marketing, but a few mistakes (misrepresenting a client, leaking bid numbers) can end it. Have an attorney review
your client agreement.

## Your own outreach (selling to subs)

**Cold email (CAN-SPAM)**
- Accurate From name and domain; subject lines that match the content (no fake "Re:" on a first touch)
- Your physical postal address in the signature
- Working opt-out honored within 10 business days (your sending tool does this; also run
  `fullbacklog mark <email> --status do_not_contact` so the engine never exports them again)
- Business addresses only

**Cold calls:** dial manually, business hours only, honor "don't call me" immediately
(`fullbacklog call <lead> --outcome do_not_call`). Check state telemarketing rules for the states you call. No
autodialers, prerecorded messages or AI voice.

**Cold texts:** don't.

**Permit data:** building permits are public records. Quote them accurately ("permit valuations as declared on
the application"), cite the source, and don't present permit value as contract value.

## Outreach to GCs on a client's behalf

- **Written authorization** in your agreement to represent the client to GCs and to use the mailbox and platform
  logins they give you.
- **Be honest about who you are.** Sign as "{Your name}, Business Development, {Client}" or "on behalf of
  {Client}". Never pretend to be the owner or an employee you aren't.
- **Every claim must be the client's own.** Project lists, references, safety numbers (EMR, OSHA logs),
  bonding capacity, licenses and certifications come from documents the client gave you. False statements on a
  prequalification form can be fraud. The client approves every prequal submission before it's sent.
- CAN-SPAM applies to these emails too: the client's address and an opt-out line.

## Bids, pricing and conflicts

- **Never share one client's numbers with anyone else, ever.** Not with another client, not with a GC beyond what
  the client submitted. Sharing or coordinating bid prices between competitors can be illegal bid rigging.
- **One client per trade per metro.** It's a selling point and it keeps you out of conflicts.
- If two clients in different trades bid the same project, keep their information separate.
- Bid follow-up asks a GC for feedback ("Were we in the ballpark? Who's running buyout?"). Don't ask a GC to reveal
  competitors' numbers.

## Certifications

- Only describe a client as certified (MBE, WBE, DBE, SBE, SDVOSB, HUBZone, 8(a)) if they hold a current
  certificate, and mention the certifying agency when it matters.
- When you help with applications, the client signs and submits. Certification fraud is a serious federal and state
  offense.

## Data handling

- Store client documents (financials, insurance, tax forms) only in the client-owned shared folder, never in email
  attachments you keep.
- Delete your copies within 30 days of the engagement ending.
- Lead databases (`*.db`) and exports contain personal data and are git-ignored. Keep it that way.

## Website

`website/privacy.html` and `website/terms.html` are templates. Replace the bracketed values and have counsel review
them before publishing.
