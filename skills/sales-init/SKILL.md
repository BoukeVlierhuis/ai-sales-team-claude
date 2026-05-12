# Seller Config Initializer

## Metadata
- **Title:** Seller Config Initializer
- **Invocation:**
    - `/sales init` — full interactive setup
    - `/sales init <section>` — regenerate one section
    - `/sales init proposition <slug>` — create/replace one proposition
    - `--from-url=<url>` — seed answers by fetching the seller's website
- **Output:** Files inside `./.sales/` in the current working directory

---

## Purpose

You scaffold and maintain a project-local `.sales/` folder that holds the seller's identity, ICP, propositions, pricing, case studies, competitive positioning, and objection responses. Every other `/sales` command that requires seller context reads from `.sales/`. Without this folder, the user gets seller-agnostic generic analysis.

The full setup walks through seven sections in this fixed order: **identity → icp → propositions (loop) → pricing → case-studies → competitive → objections**.

The example fixture at `tests/fixtures/sales-config-example/.sales/` shows the exact shape of every file. Refer to it whenever you are unsure of structure.

---

## Top-Level Routing

Parse the invocation:

| Form | Procedure |
|---|---|
| `/sales init` | Run full setup. See "Full Setup". |
| `/sales init --from-url=<url>` | Run full setup with web seeding. See "Web Seeding". |
| `/sales init identity` | Run "Identity Section" only. |
| `/sales init icp [description]` | Run "ICP Section" only. |
| `/sales init pricing` | Run "Pricing Section" only. |
| `/sales init case-studies` | Run "Case Studies Section" only. |
| `/sales init competitive` | Run "Competitive Section" only. |
| `/sales init objections` | Run "Objections Section" only. |
| `/sales init proposition <slug>` | Run "Proposition Section" for that slug. |
| any of the above `--from-url=<url>` | Same, but seed from URL first. |

If `.sales/` exists and the user invokes `/sales init` (full setup), ask:
> "An existing `.sales/` folder is present. (B)ackup to `.sales.bak-<timestamp>/` and proceed, (S)kip files that already exist, or (C)ancel?"

For section-specific or proposition-specific invocations, ask before overwriting only that file.

---

## Full Setup

Run each section procedure below in order. After each section, confirm to the user what file was written and where. At the end of the full setup:

1. Run `python scripts/verify_sales_config.py ./.sales` and report any errors.
2. Print the `.sales/` tree.
3. Print next-step pointer: `/sales prospect <url> --proposition=<slug>` using the first proposition's slug.

---

## Identity Section

Write `./.sales/identity.md`. Required H2 sections in order: `## Company`, `## Senders`, `## Voice and Tone`, `## Signature`, `## Company Bio`.

Ask the user for each field. Do not move to the next question until the current one is answered. Ask one question at a time.

1. **Company** — "What is the legal name of your company? If you operate under a different DBA, list both."
2. **Senders** — "List one or more sender personas (the people whose names will appear on outreach). For each: name, title, email, optional LinkedIn URL. You can add more later."
3. **Voice and Tone** — "Pick three adjectives that describe how you want sales communication to sound (e.g., 'direct, technical, warm'). Then add one or two sentences explaining what good sounds like."
4. **Signature** — "Paste the verbatim email signature block you want appended to outreach."
5. **Company Bio** — "Write one paragraph about the company for use in proposals and outreach context. Skip jargon — facts and outcomes only."

When all five are collected, write the file using this exact structure:

    # Identity

    ## Company
    **Legal name:** <name>
    **DBA:** <dba or "Same as legal name">

    ## Senders
    - Name: <name>
      Title: <title>
      Email: <email>
      LinkedIn: <url or "">

    ## Voice and Tone
    **Adjectives:** <a>, <b>, <c>.
    <one-to-two-sentence description>

    ## Signature
    <signature block, verbatim>

    ## Company Bio
    <one paragraph>

After writing, confirm: "Wrote `.sales/identity.md`. Regenerate with `/sales init identity`."

## ICP Section

`(filled in by Task 7)`

## Proposition Section

`(filled in by Task 8)`

## Pricing Section

`(filled in by Task 9)`

## Case Studies Section

`(filled in by Task 10)`

## Competitive Section

`(filled in by Task 11)`

## Objections Section

`(filled in by Task 12)`

## Web Seeding (`--from-url`)

`(filled in by Task 13)`

---

## Quality Standards

- Every file written must validate against `python scripts/verify_sales_config.py`. If validation fails, fix and re-write before reporting success.
- Use the Write tool for new files; use Edit for partial updates.
- Mirror the structure of the fixture at `tests/fixtures/sales-config-example/.sales/` exactly — same H2 headers, same order.
- After writing each file, briefly confirm to the user what was written and how to regenerate it later.
