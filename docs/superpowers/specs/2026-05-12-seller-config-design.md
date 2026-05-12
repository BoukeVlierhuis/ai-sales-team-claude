# Seller Config — Design Spec

**Date:** 2026-05-12
**Status:** Approved for planning
**Owner:** Bouke
**Project:** ai-sales-team-claude

---

## Problem

The 13 sales skills in this project (research, qualify, prospect, contacts, outreach, followup, prep, proposal, objections, competitors, icp, report, report-pdf) operate on a prospect URL but have no systematic awareness of the seller — who the user is, what they sell, who they target, their pricing, case studies, competitive positioning, or objection responses. Every invocation is effectively seller-agnostic, producing generic analysis that the user must mentally re-contextualize against their own business.

The `sales-icp` skill already produces an `IDEAL-CUSTOMER-PROFILE.md` file, but no downstream skill reads it. Other dimensions of seller context (propositions, pricing, case studies, competitive positioning, identity) have no home at all.

## Goal

Add a project-local seller config that every applicable skill consumes, so that prospect scoring, outreach personalization, proposal generation, and objection handling are all calibrated to the user's actual business.

## Non-goals

- User-global config, walk-up discovery, env-var overrides — project-local only.
- Multi-seller / agency mode — one config per project.
- Manifest files, YAML schema, schema validation libraries — convention is the schema.
- Auto-detection of which proposition fits a prospect — explicit `--proposition=<slug>` flag only.
- Preserving the legacy top-level `IDEAL-CUSTOMER-PROFILE.md` output — it moves into `.sales/icp.md`.

---

## 1. Folder Structure and File Contracts

The seller config lives at `.sales/` in the project root (the working directory where commands are run). Discovery is a direct path check; no walk-up, no env vars.

### Files

| Path | Purpose |
|---|---|
| `.sales/identity.md` | Seller legal name, sender personas (rep name, title, email), voice & tone, signature block, company bio |
| `.sales/icp.md` | Global Ideal Customer Profile — same shape as today's `IDEAL-CUSTOMER-PROFILE.md` output |
| `.sales/pricing.md` | Pricing tiers, deal-size benchmarks, discount rules, contract terms |
| `.sales/case-studies.md` | Case studies with customer names, industries, problems, solutions, metrics, optional quotes |
| `.sales/competitive.md` | Primary competitors, positioning statement vs each, displacement playbook |
| `.sales/objections.md` | Top 5–10 objections with validated responses |
| `.sales/propositions/<slug>.md` | One file per product/service. Multiple required (or at minimum one). |

All files are markdown with H2 section headers at fixed names so skills can grep reliably.

### Proposition file schema

Each `.sales/propositions/<slug>.md` must contain H2 sections in this order:

1. `## Name` — human-readable product name
2. `## Slug` — short kebab-case identifier matching the filename
3. `## Value Prop` — one-line statement of value delivered
4. `## Target Persona` — who within the ICP buys this proposition
5. `## Key Features` — bullet list
6. `## Differentiators` — what makes this beat alternatives
7. `## Ideal Use Cases` — when to lead with this proposition
8. `## Pricing Tier Reference` — pointer to the relevant tier in `pricing.md`
9. `## Success Metrics` — outcomes customers measure
10. `## Anti-Fit Signals` — when NOT to lead with this proposition

### Identity file schema

`.sales/identity.md` must contain H2 sections:

1. `## Company` — legal name, DBA if different
2. `## Senders` — list of sender personas; each has name, title, email, optional LinkedIn URL
3. `## Voice and Tone` — 3 adjectives + 2-sentence description
4. `## Signature` — verbatim email signature block
5. `## Company Bio` — one paragraph for use in proposals and outreach context

### Pricing file schema

`.sales/pricing.md` must contain:

1. `## Tiers` — table of tier name, price, what's included
2. `## Deal Size Benchmarks` — typical ACV range, minimum viable deal, enterprise threshold
3. `## Discount Rules` — when and how much
4. `## Contract Terms` — standard length, renewal, cancellation

### Case studies file schema

`.sales/case-studies.md` contains one H2 per case study. Each case study has:

- `### Customer` — name and industry
- `### Problem`
- `### Solution`
- `### Metric` — the headline result
- `### Quote` — optional pull quote

### Competitive file schema

`.sales/competitive.md` contains:

1. `## Positioning Statement` — one sentence for the whole company
2. `## Competitors` — H3 per competitor with: their target segment, their key differentiator, our win story, our loss story, displacement triggers

### Objections file schema

`.sales/objections.md` contains:

1. `## Top Objections` — H3 per objection with: the verbatim objection, the underlying concern, the validated response, supporting evidence (case study or stat)

---

## 2. `/sales init` Skill

A new skill at `skills/sales-init/SKILL.md` scaffolds and maintains `.sales/`.

### Invocation forms

| Form | Behavior |
|---|---|
| `/sales init` | Full setup. If `.sales/` exists, ask to back up first. Walks through every section. |
| `/sales init --from-url=<url>` | Full setup, seeded from corporate website (see "Web seeding" below) |
| `/sales init <section>` | Regenerate one section. Valid sections: `identity`, `icp`, `pricing`, `case-studies`, `competitive`, `objections`. Overwrites that file. `icp` may accept an optional free-text business description as a trailing argument. |
| `/sales init <section> --from-url=<url>` | Regenerate one section seeded from URL |
| `/sales init proposition <slug>` | Create or replace `.sales/propositions/<slug>.md`. If slug exists, ask before overwriting. |
| `/sales init proposition <slug> --from-url=<url>` | Same, seeded from URL (typically the product's page) |

`/sales icp <description>` remains as a back-compat alias that delegates to `/sales init icp <description>`.

### Web seeding (`--from-url`)

When `--from-url=<url>` is provided, `/sales init` performs a pre-research phase before asking questions:

1. **Fetch corporate pages.** Use `WebFetch` to retrieve homepage, `/about`, `/team`, `/pricing`, `/customers` (or `/case-studies`), `/blog`, `/careers`, `/contact`. Skip any that 404.
2. **Extract candidate values.** Parse the fetched content for each relevant section:
    - identity: company name, founders, voice/tone signals from copy, possibly sender personas from team page
    - propositions: product names and value props from homepage / product pages
    - pricing: tiers from `/pricing`
    - case-studies: customer logos and any named stories
    - competitive: positioning signals from homepage copy, any comparison pages
    - icp: industries served, customer size signals from case studies
    - objections: cannot be extracted reliably from a website; ask normally
3. **Present pre-filled drafts.** For each section, show the user the extracted draft and ask: "Confirm, edit, or skip?" rather than asking blank questions.
4. **Fall back to blank questions** for any field where extraction failed or returned low-confidence data.

The web-seeding behavior is additive — it does not change the schema of any file. It only changes the prompts inside `/sales init`.

### Question flow (full setup)

In order, with seeded values shown when available:

1. **Identity** — company name, primary sender(s), voice/tone, signature, company bio
2. **ICP** — uses the existing `sales-icp` procedure (6 dimensions → negative ICP → scoring rubric → personas → playbook → competitive context). Output written to `.sales/icp.md`.
3. **Propositions** — loop: slug, name, value prop, target persona, features, differentiators, ideal use cases, pricing tier reference, success metrics, anti-fit signals. Minimum one proposition required to exit setup.
4. **Pricing** — tiers, deal-size benchmarks, discount rules, contract terms
5. **Case studies** — at least one; each with customer name, industry, problem, solution, metric, optional quote
6. **Competitive** — positioning statement + top 3–5 competitors
7. **Objections** — top 5–10 objections with validated responses

### Behavior rules

- Idempotent. Existing files are preserved unless explicitly regenerated.
- Each section confirms what was written and to which path.
- At the end, prints the `.sales/` tree and a next-step pointer: `/sales prospect <url> --proposition=<slug>`.
- The existing `/sales icp <description>` command becomes an alias for `/sales init icp <description>`. The standalone `sales-icp` skill's procedure moves inside `sales-init`; its SKILL.md file is rewritten to delegate to `/sales init icp`.

---

## 3. Command Grammar Update

Every command that needs a proposition takes a required `--proposition=<slug>` flag.

| Command | Requires `.sales/`? | Requires `--proposition`? |
|---|---|---|
| `/sales init [section]` | no (creates it) | no |
| `/sales quick <url>` | no | no |
| `/sales research <url>` | no | no |
| `/sales competitors <url>` | no (reads if present) | no |
| `/sales contacts <url>` | yes | yes |
| `/sales qualify <url>` | yes | yes |
| `/sales prospect <url>` | yes | yes |
| `/sales outreach <prospect>` | yes | yes |
| `/sales followup <prospect>` | yes | yes |
| `/sales prep <url>` | yes | yes |
| `/sales proposal <client>` | yes | yes |
| `/sales objections <topic>` | yes | yes |
| `/sales report` | yes | no |
| `/sales report-pdf` | yes | no |

### Error messages

- Missing `.sales/` when required: `"No seller config found. Run /sales init to set one up."`
- Missing `--proposition` when required: `"Which proposition? Available: foo, bar, baz. Re-run with --proposition=<slug>."`
- Unknown proposition slug: `"Proposition '<slug>' not found in .sales/propositions/. Available: foo, bar, baz."`

---

## 4. Skill-by-Skill Consumption Map

Each skill that requires seller context gets a new **Phase 0: Load Seller Context** at the very top of its SKILL.md. Phase 0 lists exactly which files to Read and how they inform downstream phases.

| Skill | Files Phase 0 reads |
|---|---|
| sales-contacts | `identity.md`, `propositions/<slug>.md` |
| sales-qualify | `icp.md`, `propositions/<slug>.md` |
| sales-prospect | All six base files (`identity`, `icp`, `pricing`, `case-studies`, `competitive`, `objections`) plus the selected proposition; orchestrator passes loaded context to subagents in the discovery briefing |
| sales-outreach | `identity.md`, `propositions/<slug>.md`, `case-studies.md`, `competitive.md` |
| sales-followup | `identity.md`, `propositions/<slug>.md` |
| sales-prep | `propositions/<slug>.md`, `objections.md`, `competitive.md` |
| sales-proposal | `propositions/<slug>.md`, `pricing.md`, `case-studies.md`, `identity.md` |
| sales-objections | `objections.md`, `competitive.md`, `propositions/<slug>.md` |
| sales-competitors | `competitive.md` if present (optional, enhances output but not required) |
| sales-report / sales-report-pdf | `identity.md` for branding; aggregates prospect files |
| sales-research | none (seller-agnostic by design) |
| sales-quick | none (seller-agnostic by design) |

Subagents under `agents/` (sales-company, sales-contacts, sales-opportunity, sales-competitive, sales-strategy) receive the loaded seller context from the orchestrator inside the discovery briefing; they do not re-read files themselves.

---

## 5. How Seller Context Changes Outputs

- **Scoring.** `sales-research`, `sales-qualify`, and `sales-prospect` score the prospect against the seller's actual ICP (`.sales/icp.md`), using the weights set during `/sales init`. The 100-point rubric is no longer generic.
- **Personalization.** `sales-outreach` and `sales-followup` reference the seller's specific case studies and pricing positioning. Emails are signed by the configured sender persona using the configured voice and tone.
- **Proposals.** `sales-proposal` pulls the proposition's actual value prop, features, and pricing tier; pulls case studies that match the prospect's industry; uses the seller's competitive positioning.
- **Output headers.** Every generated artifact (`PROSPECT-ANALYSIS.md`, `OUTREACH-SEQUENCE.md`, `CLIENT-PROPOSAL.md`, etc.) gets a header block:

    ```
    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>
    ```

  So a user reading an old artifact can tell which proposition produced it and which seller config was active.

---

## 6. Migration and Testing

### Migration of existing skills

- Each of the 13 SKILL.md files is edited to add Phase 0 (where applicable per Section 4) and to use seller context in downstream phases.
- The current `skills/sales-icp/SKILL.md` is rewritten to delegate to `/sales init icp`. Its procedure (the 6-dimension ICP builder) moves into `skills/sales-init/SKILL.md` as the ICP section.
- The 5 agents under `agents/` get Phase 0 updates consistent with their corresponding skills.
- `sales/SKILL.md` (the main orchestrator) gets the new command grammar, the `/sales init` quickstart, and updated routing rules.
- `README.md` is updated: new command grammar, `/sales init` quickstart, retirement of `IDEAL-CUSTOMER-PROFILE.md` as a top-level output, mention of `--from-url` seeding.

### Testing strategy

- Add a fixture at `tests/fixtures/sales-config-example/.sales/` with a complete realistic seller config (fictional SaaS company with two propositions, two case studies, three competitors, five objections).
- For each modified skill, add a smoke test that:
    1. Runs the skill against a known prospect URL (or recorded fixture) with `--proposition=<slug>`
    2. Verifies the output file's header block contains the seller and proposition names
    3. Verifies the body references at least one detail from the seller config (e.g., a case study customer name, the configured ICP industry, a competitor name)
- Error-path tests:
    1. Run a seller-required skill without `.sales/`; assert the exact error message.
    2. Run with bad slug; assert the exact error message.
    3. Run with `.sales/` missing a file required by Phase 0; assert a clear error pointing at the missing file.
- `/sales init` tests:
    1. Run `/sales init` end-to-end with scripted answers; assert all seven files (plus at least one proposition) are written.
    2. Run `/sales init icp`; assert only `.sales/icp.md` is touched.
    3. Run `/sales init --from-url=<fixture-url>` against a recorded fixture site; assert pre-filled drafts appear in the prompts.

---

## Open questions

None at design time. The user has approved all six sections plus the `--from-url` addition. Implementation plan to follow via `writing-plans`.
