# Outreach Language Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional `## Language` field to `.sales/identity.md` so that the five outreach-oriented skills generate prospect-facing content (emails, CTAs, subject lines, LinkedIn messages) in the configured language, defaulting to Dutch (`nl`) when the field is absent.

**Architecture:** All changes are confined to Markdown skill files and one fixture file. No Python verifier changes are needed — the language field is optional and the existing verifier contracts are satisfied by identity.md already being in all five skills' Phase 0. Each skill's Phase 0 gains (a) an extended identity.md bullet that mentions `## Language`, and (b) a language-activation block with an inline Dutch writing guide inserted before the skill's first non-Phase-0 `##` heading.

**Tech Stack:** Markdown (skill files), pytest (existing test suite — no new tests).

**Spec:** `docs/superpowers/specs/2026-05-19-outreach-language-design.md`

---

## File Structure

**Modified files:**
- `tests/fixtures/sales-config-example/.sales/identity.md` — add `## Language` with value `en`
- `skills/sales-init/SKILL.md` — add language question (question 6) and `## Language` to file template
- `skills/sales-outreach/SKILL.md` — extend identity.md Phase 0 bullet; insert language-activation block
- `skills/sales-followup/SKILL.md` — extend identity.md Phase 0 bullet; insert language-activation block
- `skills/sales-proposal/SKILL.md` — extend identity.md Phase 0 bullet; insert language-activation block
- `skills/sales-prep/SKILL.md` — add identity.md to Phase 0 files list; insert language-activation block
- `skills/sales-objections/SKILL.md` — add identity.md to Phase 0 files list; insert language-activation block

**No new files. No verifier changes.**

---

## Task 1: Update the example fixture

**Files:**
- Modify: `tests/fixtures/sales-config-example/.sales/identity.md`

- [ ] **Step 1: Add `## Language` section to the fixture**

The fixture represents Lighthouse Analytics, an English-speaking company. Use Edit to append at the end of the file:

Replace:
```
## Company Bio
Lighthouse Analytics helps mid-market SaaS teams turn raw product telemetry into onboarding interventions that lift activation. Founded in 2022, used by 80+ Series A–C companies. We sit between your warehouse and your CRM and trigger plays based on user behavior in the first 14 days.
```

With:
```
## Company Bio
Lighthouse Analytics helps mid-market SaaS teams turn raw product telemetry into onboarding interventions that lift activation. Founded in 2022, used by 80+ Series A–C companies. We sit between your warehouse and your CRM and trigger plays based on user behavior in the first 14 days.

## Language
en
```

- [ ] **Step 2: Run the config verifier on the fixture**

Run: `python scripts/verify_sales_config.py tests/fixtures/sales-config-example/.sales`
Expected: exit code 0, no output.

- [ ] **Step 3: Run the full test suite**

Run: `pytest tests/ -v`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/sales-config-example/.sales/identity.md
git commit -m "feat(fixture): add Language=en to Lighthouse Analytics identity"
```

---

## Task 2: Update `/sales init` identity section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

The Identity Section currently documents five questions and a five-section file template. Add a sixth question and extend the template.

- [ ] **Step 1: Add the language question to the numbered list**

Use Edit to replace:
```
5. **Company Bio** — "Write one paragraph about the company for use in proposals and outreach context. Skip jargon — facts and outcomes only."

When all five are collected, write the file using this exact structure:
```

With:
```
5. **Company Bio** — "Write one paragraph about the company for use in proposals and outreach context. Skip jargon — facts and outcomes only."
6. **Language** — "In welke taal wil je outreach genereren? Voer een ISO 639-1 code in (`nl` voor Nederlands, `en` voor Engels). Druk Enter voor de default (`nl`)." If the user presses Enter or leaves the field blank, use `nl`.

When all six fields are collected, write the file using this exact structure:
```

- [ ] **Step 2: Add `## Language` to the file template**

Use Edit to replace:
```
    ## Company Bio
    <one paragraph>

After writing, confirm: "Wrote `.sales/identity.md`. Regenerate with `/sales init identity`."
```

With:
```
    ## Company Bio
    <one paragraph>

    ## Language
    <ISO 639-1 code, e.g. nl or en>

After writing, confirm: "Wrote `.sales/identity.md`. Regenerate with `/sales init identity`."
```

- [ ] **Step 3: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add Language field to identity section"
```

---

## Task 3: sales-outreach — Phase 0 language extension

**Files:**
- Modify: `skills/sales-outreach/SKILL.md`

- [ ] **Step 1: Extend the identity.md bullet in Phase 0**

Use Edit to replace:
```
- `.sales/identity.md` — Senders block (use the configured sender persona for from-name, signature, and LinkedIn handle); Voice and Tone (every email must match these adjectives)
```

With:
```
- `.sales/identity.md` — Senders block (use the configured sender persona for from-name, signature, and LinkedIn handle); Voice and Tone (every email must match these adjectives); and optionally `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code and activate the writing-guidance block at the end of this Phase 0.
```

- [ ] **Step 2: Insert the language-activation block**

Use Edit to replace:
```
    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

## When This Skill Is Invoked
```

With:
```
    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

**Taalinstelling.** Lees `## Language` uit identity.md (default: `nl` als de sectie ontbreekt of leeg is). Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten, CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`) blijven in het Engels.

Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

- **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
- **`nl` (Nederlands, default):**
    - **Aanhef:** gebruik "je/jij" tenzij de prospect expliciet formeel zakelijk is (dan "u"). Wees consistent door de hele reeks.
    - **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten. Begin altijd met een specifieke observatie over de prospect.
    - **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is acceptabel. Geen uitroeptekens.
    - **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van "Would it be worth a quick call?"
    - **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de prospect dat zelf gebruikt.
    - **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten, niet als een marketeer. Geen wollige omschrijvingen.
    - **Handtekening:** gebruik de `## Signature` uit identity.md verbatim.
- **Andere code:** schrijf in die taal met dezelfde principes als `nl`: direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.

## When This Skill Is Invoked
```

- [ ] **Step 3: Verify the Phase 0 contract still passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-outreach || echo "OK"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add skills/sales-outreach/SKILL.md
git commit -m "feat(sales-outreach): add language-aware writing guidance to Phase 0"
```

---

## Task 4: sales-followup — Phase 0 language extension

**Files:**
- Modify: `skills/sales-followup/SKILL.md`

- [ ] **Step 1: Extend the identity.md bullet in Phase 0**

Use Edit to replace:
```
- `.sales/identity.md` — Sender + Voice and Tone for follow-up emails
```

With:
```
- `.sales/identity.md` — Sender + Voice and Tone for follow-up emails; and optionally `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code and activate the writing-guidance block at the end of this Phase 0.
```

- [ ] **Step 2: Insert the language-activation block**

Use Edit to replace (the four indented lines plus the blank line plus the `## Invocation` heading — stop there, do not include the code block that follows):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    ## Invocation

With (same header block, language-activation block inserted between, then the heading):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    **Taalinstelling.** Lees `## Language` uit identity.md (default: `nl` als de sectie ontbreekt of leeg is). Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten, CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`) blijven in het Engels.

    Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

    - **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
    - **`nl` (Nederlands, default):**
        - **Aanhef:** gebruik "je/jij" tenzij de prospect expliciet formeel zakelijk is (dan "u"). Wees consistent door de hele reeks.
        - **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten. Begin altijd met een specifieke observatie over de prospect.
        - **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is acceptabel. Geen uitroeptekens.
        - **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van "Would it be worth a quick call?"
        - **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de prospect dat zelf gebruikt.
        - **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten, niet als een marketeer. Geen wollige omschrijvingen.
        - **Handtekening:** gebruik de `## Signature` uit identity.md verbatim.
    - **Andere code:** schrijf in die taal met dezelfde principes als `nl`: direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.

    ## Invocation

The match must be unique within `skills/sales-followup/SKILL.md`. The combination of the four indented header lines + blank + `## Invocation` appears only once in that file.

- [ ] **Step 3: Verify the Phase 0 contract still passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-followup || echo "OK"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add skills/sales-followup/SKILL.md
git commit -m "feat(sales-followup): add language-aware writing guidance to Phase 0"
```

---

## Task 5: sales-proposal — Phase 0 language extension

**Files:**
- Modify: `skills/sales-proposal/SKILL.md`

- [ ] **Step 1: Extend the identity.md bullet in Phase 0**

Use Edit to replace:
```
- `.sales/identity.md` — Company Bio for the "About Us" section; Sender persona for the cover page.
```

With:
```
- `.sales/identity.md` — Company Bio for the "About Us" section; Sender persona for the cover page; and optionally `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code and activate the writing-guidance block at the end of this Phase 0.
```

- [ ] **Step 2: Insert the language-activation block**

Use Edit to replace (four indented header lines + blank + `## Invocation` heading — stop there):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    ## Invocation

With (header block + language-activation block + heading):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    **Taalinstelling.** Lees `## Language` uit identity.md (default: `nl` als de sectie ontbreekt of leeg is). Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten, CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`) blijven in het Engels.

    Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

    - **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
    - **`nl` (Nederlands, default):**
        - **Aanhef:** gebruik "je/jij" tenzij de prospect expliciet formeel zakelijk is (dan "u"). Wees consistent door de hele reeks.
        - **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten. Begin altijd met een specifieke observatie over de prospect.
        - **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is acceptabel. Geen uitroeptekens.
        - **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van "Would it be worth a quick call?"
        - **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de prospect dat zelf gebruikt.
        - **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten, niet als een marketeer. Geen wollige omschrijvingen.
        - **Handtekening:** gebruik de `## Signature` uit identity.md verbatim.
    - **Andere code:** schrijf in die taal met dezelfde principes als `nl`: direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.

    ## Invocation

- [ ] **Step 3: Verify the Phase 0 contract still passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-proposal || echo "OK"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add skills/sales-proposal/SKILL.md
git commit -m "feat(sales-proposal): add language-aware writing guidance to Phase 0"
```

---

## Task 6: sales-prep — Phase 0 language extension

**Files:**
- Modify: `skills/sales-prep/SKILL.md`

Note: `identity.md` is NOT currently in sales-prep's Phase 0 files list. This task adds it.

- [ ] **Step 1: Add identity.md to the Phase 0 files list**

Use Edit to replace:
```
**Files to load:**
- `.sales/propositions/<slug>.md` — proposition details, ideal use cases, anti-fit signals; the prep brief must anticipate which proposition aspects will land and which will not
- `.sales/objections.md` — pre-loaded responses for objections the prospect is likely to raise
- `.sales/competitive.md` — if the prospect uses a known competitor, surface our win story and displacement triggers in the prep brief
```

With:
```
**Files to load:**
- `.sales/propositions/<slug>.md` — proposition details, ideal use cases, anti-fit signals; the prep brief must anticipate which proposition aspects will land and which will not
- `.sales/objections.md` — pre-loaded responses for objections the prospect is likely to raise
- `.sales/competitive.md` — if the prospect uses a known competitor, surface our win story and displacement triggers in the prep brief
- `.sales/identity.md` — optionally `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code and activate the writing-guidance block at the end of this Phase 0.
```

- [ ] **Step 2: Insert the language-activation block**

Use Edit to replace (four indented header lines + blank + `## Invocation` heading — stop there):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    ## Invocation

With (header block + language-activation block + heading):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    **Taalinstelling.** Lees `## Language` uit identity.md (default: `nl` als de sectie ontbreekt of leeg is). Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten, CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`) blijven in het Engels.

    Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

    - **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
    - **`nl` (Nederlands, default):**
        - **Aanhef:** gebruik "je/jij" tenzij de prospect expliciet formeel zakelijk is (dan "u"). Wees consistent door de hele reeks.
        - **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten. Begin altijd met een specifieke observatie over de prospect.
        - **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is acceptabel. Geen uitroeptekens.
        - **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van "Would it be worth a quick call?"
        - **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de prospect dat zelf gebruikt.
        - **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten, niet als een marketeer. Geen wollige omschrijvingen.
        - **Handtekening:** gebruik de `## Signature` uit identity.md verbatim.
    - **Andere code:** schrijf in die taal met dezelfde principes als `nl`: direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.

    ## Invocation

- [ ] **Step 3: Verify the Phase 0 contract still passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-prep || echo "OK"`
Expected: `OK` (the contract does not require identity.md for sales-prep; the verifier only checks that existing required files are present, not that extra files are absent).

- [ ] **Step 4: Commit**

```bash
git add skills/sales-prep/SKILL.md
git commit -m "feat(sales-prep): add identity.md and language-aware writing guidance to Phase 0"
```

---

## Task 7: sales-objections — Phase 0 language extension

**Files:**
- Modify: `skills/sales-objections/SKILL.md`

Note: `identity.md` is NOT currently in sales-objections's Phase 0 files list. This task adds it.

- [ ] **Step 1: Add identity.md to the Phase 0 files list**

Use Edit to replace:
```
**Files to load:**
- `.sales/objections.md` — seed objection list; the playbook generated for the prospect must build ON this list, not duplicate it
- `.sales/competitive.md` — competitive context for any "Why not <competitor>?" objections
- `.sales/propositions/<slug>.md` — Anti-Fit Signals; if any signal applies to the prospect, surface it as a likely objection
```

With:
```
**Files to load:**
- `.sales/objections.md` — seed objection list; the playbook generated for the prospect must build ON this list, not duplicate it
- `.sales/competitive.md` — competitive context for any "Why not <competitor>?" objections
- `.sales/propositions/<slug>.md` — Anti-Fit Signals; if any signal applies to the prospect, surface it as a likely objection
- `.sales/identity.md` — optionally `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code and activate the writing-guidance block at the end of this Phase 0.
```

- [ ] **Step 2: Insert the language-activation block**

Use Edit to replace (four indented header lines + blank + `## Invocation` heading — stop there):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    ## Invocation

With (header block + language-activation block + heading):

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>

    **Taalinstelling.** Lees `## Language` uit identity.md (default: `nl` als de sectie ontbreekt of leeg is). Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten, CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`) blijven in het Engels.

    Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

    - **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
    - **`nl` (Nederlands, default):**
        - **Aanhef:** gebruik "je/jij" tenzij de prospect expliciet formeel zakelijk is (dan "u"). Wees consistent door de hele reeks.
        - **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten. Begin altijd met een specifieke observatie over de prospect.
        - **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is acceptabel. Geen uitroeptekens.
        - **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van "Would it be worth a quick call?"
        - **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de prospect dat zelf gebruikt.
        - **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten, niet als een marketeer. Geen wollige omschrijvingen.
        - **Handtekening:** gebruik de `## Signature` uit identity.md verbatim.
    - **Andere code:** schrijf in die taal met dezelfde principes als `nl`: direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.

    ## Invocation

- [ ] **Step 3: Verify the Phase 0 contract still passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-objections || echo "OK"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add skills/sales-objections/SKILL.md
git commit -m "feat(sales-objections): add identity.md and language-aware writing guidance to Phase 0"
```

---

## Task 8: End-to-end verification

No code changes. Confirm the full suite is green and the skill files are structurally sound.

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: all tests pass (3 in test_sales_config.py + 1 in test_skill_phase0.py).

- [ ] **Step 2: Run both verifiers**

Run: `python scripts/verify_sales_config.py tests/fixtures/sales-config-example/.sales && python scripts/verify_skill_phase0.py && echo "All verifiers passed"`
Expected: `All verifiers passed` (exit code 0 from both scripts).

- [ ] **Step 3: Spot-check each modified skill for structural integrity**

Run: `for f in skills/sales-outreach/SKILL.md skills/sales-followup/SKILL.md skills/sales-proposal/SKILL.md skills/sales-prep/SKILL.md skills/sales-objections/SKILL.md; do echo "=== $f ==="; grep -c '^##' "$f"; done`
Expected: each file reports a positive integer (confirms H2 headers are intact and not accidentally merged).

- [ ] **Step 4: Confirm language block appears in all five skills**

Run: `grep -l "Taalinstelling" skills/sales-outreach/SKILL.md skills/sales-followup/SKILL.md skills/sales-proposal/SKILL.md skills/sales-prep/SKILL.md skills/sales-objections/SKILL.md | wc -l`
Expected: `5`

- [ ] **Step 5: Confirm completion**

Run: `git log --oneline -8`
Expected: 7 feature commits ending with the last skill update, preceded by the fixture commit.
