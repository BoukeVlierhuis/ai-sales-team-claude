# Outreach Language Support Design

**Date:** 2026-05-19
**Scope:** Add configurable output language to the five outreach-oriented skills.

---

## Goal

Enable sellers to generate outreach content in their preferred language, configured once in `.sales/identity.md`. The default language is Dutch (`nl`). All analysis/research skills are out of scope — only prospect-facing content changes.

---

## Affected Skills

- `skills/sales-outreach/SKILL.md`
- `skills/sales-followup/SKILL.md`
- `skills/sales-proposal/SKILL.md`
- `skills/sales-prep/SKILL.md`
- `skills/sales-objections/SKILL.md`

---

## Data Model

### `## Language` in `identity.md`

An optional section containing an ISO 639-1 language code:

```markdown
## Language
nl
```

- **Optional.** If absent or empty, skills default to `nl`.
- **Not overridable** per command invocation — set once in the seller config.
- `verify_sales_config.py` does **not** enforce this field (it is optional).
- `verify_skill_phase0.py` requires no changes — `identity.md` is already in the SKILL_CONTRACT for all five skills.

### `/sales init identity` addition

After collecting the existing five fields (Company, Senders, Voice and Tone, Signature, Company Bio), the identity section asks:

> "In welke taal wil je outreach genereren? Gebruik een ISO 639-1 code (`nl` voor Nederlands, `en` voor Engels). Druk Enter voor de default (`nl`)."

If the user presses Enter or leaves blank, write `nl`. Write the value as a new `## Language` section at the end of `identity.md`.

### Fixture update

`tests/fixtures/sales-config-example/.sales/identity.md` gets `## Language\nen` — the fictional Lighthouse Analytics company is English-speaking, so example output remains in English.

---

## Phase 0 Extension (all five skills)

### 1. Extend the existing `identity.md` bullet

Replace:

```
- `.sales/identity.md` — Senders block (…); Voice and Tone (…)
```

With:

```
- `.sales/identity.md` — Senders block (…); Voice and Tone (…); and optionally
  `## Language` (ISO 639-1 code; default `nl` if absent). Read the language code
  and activate the corresponding writing-guidance block below.
```

### 2. Add a language-activation block immediately after

```markdown
**Taalinstelling.** Bepaal de taal uit `## Language` in identity.md (default: `nl`).
Genereer ALLE prospect-facing content — emails, onderwerpregels, LinkedIn-berichten,
CTAs — in die taal. Uitvoerbestandsheaders (`Seller:`, `Proposition:`, `Generated:`)
blijven in het Engels (technische metadata).

Activeer het schrijfinstructie-blok voor de gedetecteerde taalcode:

- **`nl` (Nederlands):** zie schrijfgids hieronder.
- **`en` (Engels):** bestaand gedrag, geen aanvullende instructies.
- **Andere code:** schrijf in die taal met dezelfde principes als `nl`:
  direct, zakelijk, peer-to-peer, taalspecifieke CTA-conventies.
```

---

## Nederlandse Schrijfgids (het `nl`-blok)

Dit blok wordt geactiveerd wanneer de taalcode `nl` is (of wanneer `## Language` ontbreekt):

```markdown
**`nl` — Schrijfgids Nederlands:**
- **Aanhef:** gebruik "je/jij" tenzij de ICP of prospect expliciet formeel zakelijk
  is (dan "u"). Wees consistent door de hele reeks.
- **Openingszin:** nooit "Ik hoop dat dit bericht je goed bereikt" of varianten.
  Begin altijd met een specifieke observatie over de prospect.
- **Onderwerpregels:** 4–7 woorden, direct, geen clickbait. Lowercase stijl is
  acceptabel. Geen uitroeptekens.
- **CTAs:** direct en als vraag: "Heb je 15 minuten?" — geen vertaling van
  "Would it be worth a quick call?"
- **Jargon:** gebruik vakjargon (SaaS, ARR, pipeline) als dat de norm is in de
  sector. Vermijd onnodige anglicismen voor gewone woorden: schrijf "gesprek" niet
  "call", "bericht" niet "message", "vergadering" niet "meeting" — tenzij de
  prospect dat zelf gebruikt.
- **Toon:** zakelijk maar direct. Schrijf zoals een ervaren collega zou praten,
  niet als een marketeer. Geen wollige omschrijvingen.
- **Handtekening:** gebruik de `## Signature` uit identity.md verbatim, ook als
  die in het Engels is opgesteld.
```

### What does NOT change

- Phase 1 WebSearch queries stay in English — search engines return better results regardless of output language.
- File output names (`OUTREACH-SEQUENCE.md`, etc.) stay in English.
- Output header metadata (`Seller:`, `Proposition:`, `Generated:`) stays in English.

---

## Files Changed

| File | Change |
|------|--------|
| `tests/fixtures/sales-config-example/.sales/identity.md` | Add `## Language\nen` |
| `skills/sales-init/SKILL.md` | Add language question to Identity Section |
| `skills/sales-outreach/SKILL.md` | Extend Phase 0 with language block + NL schrijfgids |
| `skills/sales-followup/SKILL.md` | Extend Phase 0 with language block + NL schrijfgids |
| `skills/sales-proposal/SKILL.md` | Extend Phase 0 with language block + NL schrijfgids |
| `skills/sales-prep/SKILL.md` | Extend Phase 0 with language block + NL schrijfgids |
| `skills/sales-objections/SKILL.md` | Extend Phase 0 with language block + NL schrijfgids |

**Not changed:** `verify_sales_config.py`, `verify_skill_phase0.py`, `agents/`, `sales/SKILL.md`

**No new files.**

---

## Out of Scope

- Research/analysis skills (`sales-research`, `sales-qualify`, `sales-contacts`, `sales-prospect`, `sales-report`, `sales-competitors`)
- Per-command language override flag
- Multi-language seller configs (one language per seller config)
- Automated tests for language output correctness (skill instruction changes have no machine-verifiable test)
