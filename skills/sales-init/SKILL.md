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

`(filled in by Task 6)`

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
