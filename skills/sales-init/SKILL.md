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

Write `./.sales/icp.md`.

**Input:** The user may supply a free-text business description as a trailing argument: `/sales init icp <description>`. If absent, ask once: "Describe what you sell and to whom — one paragraph is enough."

**Procedure:** Run the full ICP-builder procedure (the same procedure that today's `sales-icp` skill uses). Produce the following sections in order:

1. `## ICP Summary` — 2–3 paragraph executive summary
2. `## Firmographic Criteria` — table with columns Criterion, Ideal Range, Why It Matters, Red Flag
3. `## Technographic Profile`
4. `## Behavioral Signals`
5. `## Pain Point Map` — ranked list (top 3–5)
6. `## Budget Qualifiers`
7. `## Channel Strategy`
8. `## Negative ICP` — 8–10 disqualification criteria
9. `## ICP Scoring Rubric` — 100-point rubric across Firmographic, Technographic, Pain, Budget, Contact Access, Timing
10. `## Buyer Personas` — 2–3 personas
11. `## Prospecting Playbook` — where to find them, search strings, prioritization, timing
12. `## Competitive Context` — brief competitive landscape

**Quality rules** (carried over from the original sales-icp procedure):

- Every criterion must be SPECIFIC (no "medium-sized companies" — use exact ranges).
- Every recommendation must be ACTIONABLE (no "leverage social selling" — say exactly what to do).
- Use tables wherever structured data fits.
- Cite reasoning — explain WHY each criterion matters.
- If a detail is missing from the user's description, state your assumption explicitly.

**Research step:** Before producing the ICP, run these `WebSearch` queries to ground recommendations in market reality:

- `[product category] market size TAM`
- `[product category] competitors alternatives`
- `[product category] trends 2026`
- `[product category] buying process B2B`
- `[product category] pricing benchmarks`

**Do not ask more than one clarifying question.** Make informed assumptions and state them.

The fixture at `tests/fixtures/sales-config-example/.sales/icp.md` shows the minimum structure (an abbreviated ICP). For real users, produce a substantive document of 300–400 lines.

After writing, confirm: "Wrote `.sales/icp.md`. Regenerate with `/sales init icp [description]`."

## Proposition Section

Write `./.sales/propositions/<slug>.md`. Loop this section during full setup until the user declines to add another proposition. A minimum of one proposition is required to complete full setup.

**For each proposition, ask in order:**

1. **Slug** — "Short kebab-case identifier (e.g., `onboarding-suite`). This becomes the filename and the `--proposition=<slug>` argument."
2. **Name** — "Human-readable product name."
3. **Value Prop** — "One sentence: what value is delivered, to whom, with what measurable outcome."
4. **Target Persona** — "Who inside the ICP buys this specifically?"
5. **Key Features** — "List the 4–8 most important features."
6. **Differentiators** — "Why does this beat the alternatives the buyer would compare it against?"
7. **Ideal Use Cases** — "When should a salesperson lead with this proposition?"
8. **Pricing Tier Reference** — "Which tier in `pricing.md` does this typically map to?"
9. **Success Metrics** — "What outcomes do successful customers measure?"
10. **Anti-Fit Signals** — "When should a salesperson NOT lead with this proposition?"

Before writing, check whether `./.sales/propositions/<slug>.md` already exists. If it does, ask: "Replace existing proposition '<slug>'? (Y/N)".

Write the file using this exact structure:

    # <Name>

    ## Name
    <Name>

    ## Slug
    <slug>

    ## Value Prop
    <one sentence>

    ## Target Persona
    <description>

    ## Key Features
    - <feature>
    - <feature>

    ## Differentiators
    - <differentiator>
    - <differentiator>

    ## Ideal Use Cases
    - <use case>
    - <use case>

    ## Pricing Tier Reference
    <Tier name(s) from pricing.md>

    ## Success Metrics
    - <metric>
    - <metric>

    ## Anti-Fit Signals
    - <signal>
    - <signal>

After writing, confirm: "Wrote `.sales/propositions/<slug>.md`. Add more with `/sales init proposition <new-slug>`."

In full-setup mode, after writing one proposition ask: "Add another proposition? (Y/N)". Loop until N.

## Pricing Section

Write `./.sales/pricing.md`. Required H2 sections: `## Tiers`, `## Deal Size Benchmarks`, `## Discount Rules`, `## Contract Terms`.

Ask the user:

1. **Tiers** — "List your published pricing tiers. For each: name, price (or 'Custom'), and a one-line description of what's included."
2. **Deal Size Benchmarks** — "Typical ACV? Minimum viable deal? At what dollar amount does a deal cross into enterprise?"
3. **Discount Rules** — "When do you discount and by how much? What requires approval?"
4. **Contract Terms** — "Standard term length, renewal behavior, cancellation policy."

Write the file using this exact structure:

    # Pricing

    ## Tiers

    | Tier | Price | Includes |
    |---|---|---|
    | <tier> | <price> | <description> |

    ## Deal Size Benchmarks
    - Typical ACV: <amount>
    - Minimum viable deal: <amount>
    - Enterprise threshold: <amount>

    ## Discount Rules
    - <rule>
    - <rule>

    ## Contract Terms
    - Standard term: <length>
    - Renewal: <behavior>
    - Cancellation: <policy>

After writing, confirm: "Wrote `.sales/pricing.md`. Regenerate with `/sales init pricing`."

## Case Studies Section

Write `./.sales/case-studies.md`. The file contains one H2 per case study. A minimum of one case study is required.

For each case study, ask:

1. **Customer** — "Customer name and industry."
2. **Problem** — "What problem did they have, in one or two sentences? Use their words where possible."
3. **Solution** — "What did they buy and how did they use it?"
4. **Metric** — "What is the headline result? Quantified."
5. **Quote** — "Optional: pull quote from the customer, with their title."

Loop: ask "Add another case study? (Y/N)". Stop when N.

Write the file using this structure:

    # Case Studies

    ## <Customer Name> (<industry>, optional stage)
    ### Customer
    <name and industry sentence>
    ### Problem
    <problem>
    ### Solution
    <solution>
    ### Metric
    <headline result>
    ### Quote
    > "<quote>" — <name>, <title>

After writing, confirm: "Wrote `.sales/case-studies.md`. Regenerate with `/sales init case-studies`."

## Competitive Section

Write `./.sales/competitive.md`. Required H2 sections: `## Positioning Statement`, `## Competitors`.

Ask the user:

1. **Positioning Statement** — "In one sentence, how do you position against the broader market?"
2. **Competitors** — "List 3–5 competitors you most often encounter in deals." Loop for each:
    - Their target segment
    - Their key differentiator
    - Our win story (one sentence on how we win against them)
    - Our loss story (one sentence on when they win)
    - Displacement triggers (what makes a customer switch from them to us)

Write the file using this structure:

    # Competitive

    ## Positioning Statement
    <one sentence>

    ## Competitors

    ### <Competitor Name>
    - **Their target:** <description>
    - **Their differentiator:** <description>
    - **Our win story:** "<sentence>"
    - **Our loss story:** <sentence>
    - **Displacement triggers:** <description>

After writing, confirm: "Wrote `.sales/competitive.md`. Regenerate with `/sales init competitive`."

## Objections Section

Write `./.sales/objections.md`. Required H2 section: `## Top Objections`. List 5–10 objections.

For each objection, ask:

1. **Objection** — "What does the prospect say, verbatim?"
2. **Underlying concern** — "What is the real concern behind that wording?"
3. **Response** — "What is the response that has worked? Be specific."
4. **Evidence** — "What case study, stat, or proof point backs up the response?"

Loop: ask "Add another objection? (Y/N)". Stop at N or after 10.

Write the file using this structure:

    # Objection Playbook

    ## Top Objections

    ### "<objection verbatim>"
    **Underlying concern:** <concern>
    **Response:** <response>
    **Evidence:** <evidence>

After writing, confirm: "Wrote `.sales/objections.md`. Regenerate with `/sales init objections`."

## Web Seeding (`--from-url`)

When the user passes `--from-url=<url>`, run a pre-research phase before any questions. The goal: prefill candidate answers so the user reviews/edits instead of typing from scratch.

### Pre-research procedure

1. **Fetch pages.** Use `WebFetch` to retrieve the following from the supplied URL (skip any that 404):
    - `/` (homepage)
    - `/about`, `/about-us`, `/company`
    - `/team`, `/leadership`
    - `/pricing`, `/plans`
    - `/customers`, `/case-studies`
    - `/blog` (first page)
    - `/careers`
    - `/contact`

2. **Extract candidate values per section:**

    | Section | What to extract | From |
    |---|---|---|
    | identity.company | Legal name + DBA | Homepage footer, About page, /legal if visible |
    | identity.senders | Names + titles + emails | Team/leadership pages |
    | identity.voice_and_tone | Inferred adjectives | Homepage and blog copy — analyze tone |
    | identity.company_bio | One-paragraph description | About page first paragraph |
    | propositions | Product names + value props | Homepage product sections, product pages |
    | pricing.tiers | Tier names + prices + inclusions | /pricing page |
    | case-studies | Customer names + metrics + quotes | /customers, /case-studies |
    | competitive.positioning | Inferred positioning statement | Homepage hero copy |
    | competitive.competitors | Comparison pages if any | /vs-* pages or comparison content |
    | icp | Industries served + customer size signals | Case studies, customer logos |
    | objections | (cannot be reliably extracted) | — fall back to asking |

3. **Present pre-filled drafts.** For each section, show the extracted draft and ask: "Here's what I extracted: [draft]. (A)ccept as-is, (E)dit, (S)kip, or (B)lank to fill from scratch?" Process each section using the same write procedure described above, but starting from the candidate values instead of an empty form.

4. **Fall back to blank questions** for any field where extraction failed or returned low-confidence data. Mark uncertain extractions with `<!-- low-confidence: review -->` in the draft so the user sees what to scrutinize.

### Confidence rules

- Mark extractions as low-confidence when:
    - The source page returned a non-200 status
    - The page contains no clear matching content (e.g., no `/pricing` page found)
    - The extracted text is generic marketing copy without specifics
- Mark as high-confidence when the source page exists, contains structured content (table, list, named entities), and the extraction is verbatim or near-verbatim.

The web seeding behavior changes ONLY the prompts inside the init procedure. It does not change the schema of any file or which sections are required.

---

## Quality Standards

- Every file written must validate against `python scripts/verify_sales_config.py`. If validation fails, fix and re-write before reporting success.
- Use the Write tool for new files; use Edit for partial updates.
- Mirror the structure of the fixture at `tests/fixtures/sales-config-example/.sales/` exactly — same H2 headers, same order.
- After writing each file, briefly confirm to the user what was written and how to regenerate it later.
