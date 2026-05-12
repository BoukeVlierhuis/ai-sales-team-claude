# Seller Config Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every applicable `/sales` skill consume a project-local `.sales/` seller config (ICP, propositions, identity, pricing, case studies, competitive, objections), so prospect scoring, outreach personalization, and proposals are calibrated to the user's actual business.

**Architecture:** Add a new `sales-init` skill that scaffolds `.sales/` interactively (with optional `--from-url` web seeding). Add a Python verifier (`scripts/verify_sales_config.py`) that lints `.sales/` and SKILL.md "Phase 0" sections — this verifier is the test for every migration task. Migrate the 13 existing skills + 5 agents + main orchestrator + README to consume seller context via a "Phase 0: Load Seller Context" preamble.

**Tech Stack:** Markdown (skill files), Python 3 (verifier + existing scripts), pytest (new test framework), `WebFetch` / `WebSearch` (used by skills at runtime).

**Spec:** `docs/superpowers/specs/2026-05-12-seller-config-design.md`

---

## File Structure

**New files:**
- `skills/sales-init/SKILL.md` — new init skill
- `scripts/verify_sales_config.py` — lints `.sales/` folder structure
- `scripts/verify_skill_phase0.py` — lints SKILL.md files for Phase 0 contract
- `tests/__init__.py`, `tests/conftest.py` — pytest harness
- `tests/test_sales_config.py` — runs the verifiers against fixtures
- `tests/fixtures/sales-config-example/.sales/identity.md`
- `tests/fixtures/sales-config-example/.sales/icp.md`
- `tests/fixtures/sales-config-example/.sales/pricing.md`
- `tests/fixtures/sales-config-example/.sales/case-studies.md`
- `tests/fixtures/sales-config-example/.sales/competitive.md`
- `tests/fixtures/sales-config-example/.sales/objections.md`
- `tests/fixtures/sales-config-example/.sales/propositions/onboarding-suite.md`
- `tests/fixtures/sales-config-example/.sales/propositions/analytics-platform.md`

**Modified files:**
- `requirements.txt` — add pytest
- `sales/SKILL.md` — new command grammar, error rules, routing
- `skills/sales-icp/SKILL.md` — rewritten as delegating alias to `/sales init icp`
- `skills/sales-contacts/SKILL.md` — add Phase 0
- `skills/sales-qualify/SKILL.md` — add Phase 0
- `skills/sales-outreach/SKILL.md` — add Phase 0
- `skills/sales-followup/SKILL.md` — add Phase 0
- `skills/sales-prep/SKILL.md` — add Phase 0
- `skills/sales-proposal/SKILL.md` — add Phase 0
- `skills/sales-objections/SKILL.md` — add Phase 0
- `skills/sales-prospect/SKILL.md` — add Phase 0 + pass briefing to subagents
- `skills/sales-competitors/SKILL.md` — optional Phase 0
- `skills/sales-report/SKILL.md` — add Phase 0 (identity only)
- `skills/sales-report-pdf/SKILL.md` — add Phase 0 (identity only)
- `agents/sales-company.md`, `agents/sales-contacts.md`, `agents/sales-opportunity.md`, `agents/sales-competitive.md`, `agents/sales-strategy.md` — consume context from orchestrator briefing
- `README.md` — new commands, init quickstart, retire `IDEAL-CUSTOMER-PROFILE.md`

**Conventions for all SKILL.md edits in Phase 4:**
Every modified skill gets a new `## Phase 0: Load Seller Context` section inserted immediately after the skill's opening prose (before the first existing `## Phase` or `## When This Skill Is Invoked`). The Phase 0 block follows this exact template:

```markdown
## Phase 0: Load Seller Context

**Requires `.sales/` (project-local seller config).** If missing, error: `"No seller config found. Run /sales init to set one up."`

**Requires `--proposition=<slug>` argument.** If missing, list available propositions from `.sales/propositions/*.md` and error: `"Which proposition? Available: <slug list>. Re-run with --proposition=<slug>."` If slug unknown, error: `"Proposition '<slug>' not found in .sales/propositions/. Available: <slug list>."`

**Files to load:**
<per-skill list>

Use these files throughout the procedure below. Every generated output file includes this header block at the top:

    Seller: <identity.company>
    Proposition: <slug> — <name>
    ICP: .sales/icp.md
    Generated: <date>
```

The per-skill file list comes from Section 4 of the spec.

---

## Phase 1: Foundation

### Task 1: Test harness and pytest dependency

**Files:**
- Modify: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Add pytest to requirements.txt**

```
reportlab>=4.0
beautifulsoup4>=4.12
requests>=2.31
pytest>=8.0
```

- [ ] **Step 2: Create `tests/__init__.py`**

```python
```

(Empty file; pytest treats `tests/` as a package.)

- [ ] **Step 3: Create `tests/conftest.py`**

```python
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def example_config_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "sales-config-example" / ".sales"
```

- [ ] **Step 4: Install pytest and verify it runs**

Run: `pip install -r requirements.txt && pytest tests/ -v`
Expected: `no tests ran in 0.XXs` (exit code 0 or 5; no tests yet)

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/__init__.py tests/conftest.py
git commit -m "chore: add pytest dependency and test harness"
```

---

### Task 2: Seller config verifier

**Files:**
- Create: `scripts/verify_sales_config.py`
- Create: `tests/test_sales_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_sales_config.py`:

```python
import subprocess
import sys
from pathlib import Path

import pytest


VERIFY_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verify_sales_config.py"


def _run_verifier(config_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(config_dir)],
        capture_output=True,
        text=True,
    )


def test_example_fixture_validates(example_config_dir: Path) -> None:
    result = _run_verifier(example_config_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_required_file_reports_error(tmp_path: Path) -> None:
    config = tmp_path / ".sales"
    (config / "propositions").mkdir(parents=True)
    (config / "identity.md").write_text("## Company\nExample Co\n")
    result = _run_verifier(config)
    assert result.returncode != 0
    assert "icp.md" in result.stdout + result.stderr


def test_missing_required_section_reports_error(tmp_path: Path) -> None:
    config = tmp_path / ".sales"
    (config / "propositions").mkdir(parents=True)
    for name in ("identity.md", "icp.md", "pricing.md", "case-studies.md", "competitive.md", "objections.md"):
        (config / name).write_text("# placeholder with no H2\n")
    (config / "propositions" / "demo.md").write_text("# placeholder\n")
    result = _run_verifier(config)
    assert result.returncode != 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sales_config.py -v`
Expected: tests fail because `scripts/verify_sales_config.py` does not exist and `tests/fixtures/sales-config-example/.sales/` does not exist.

- [ ] **Step 3: Implement the verifier**

Create `scripts/verify_sales_config.py`:

```python
"""Lint a project-local .sales/ seller config folder.

Usage: python scripts/verify_sales_config.py <path-to-.sales-folder>

Exits 0 if the folder is well-formed, 1 otherwise. Errors print to stdout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES: dict[str, list[str]] = {
    "identity.md": ["## Company", "## Senders", "## Voice and Tone", "## Signature", "## Company Bio"],
    "icp.md": ["## ICP Summary", "## Firmographic Criteria"],
    "pricing.md": ["## Tiers", "## Deal Size Benchmarks", "## Discount Rules", "## Contract Terms"],
    "case-studies.md": ["## "],
    "competitive.md": ["## Positioning Statement", "## Competitors"],
    "objections.md": ["## Top Objections"],
}


PROPOSITION_SECTIONS: list[str] = [
    "## Name",
    "## Slug",
    "## Value Prop",
    "## Target Persona",
    "## Key Features",
    "## Differentiators",
    "## Ideal Use Cases",
    "## Pricing Tier Reference",
    "## Success Metrics",
    "## Anti-Fit Signals",
]


def _check_sections(text: str, required: list[str]) -> list[str]:
    missing: list[str] = []
    for header in required:
        pattern = re.compile(rf"^{re.escape(header)}\b", re.MULTILINE)
        if not pattern.search(text):
            missing.append(header)
    return missing


def verify(config_dir: Path) -> list[str]:
    errors: list[str] = []
    if not config_dir.is_dir():
        return [f"not a directory: {config_dir}"]

    for filename, required_sections in REQUIRED_FILES.items():
        path = config_dir / filename
        if not path.is_file():
            errors.append(f"missing required file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for missing in _check_sections(text, required_sections):
            errors.append(f"{filename}: missing section '{missing}'")

    propositions_dir = config_dir / "propositions"
    if not propositions_dir.is_dir():
        errors.append("missing required folder: propositions/")
        return errors

    prop_files = sorted(p for p in propositions_dir.glob("*.md") if not p.name.startswith("_"))
    if not prop_files:
        errors.append("propositions/: at least one proposition file required")

    for prop in prop_files:
        text = prop.read_text(encoding="utf-8")
        for missing in _check_sections(text, PROPOSITION_SECTIONS):
            errors.append(f"propositions/{prop.name}: missing section '{missing}'")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_sales_config.py <path-to-.sales-folder>", file=sys.stderr)
        return 2
    errors = verify(Path(argv[1]))
    for err in errors:
        print(err)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run tests again — `test_missing_required_file_reports_error` should pass, others still fail**

Run: `pytest tests/test_sales_config.py -v`
Expected: `test_missing_required_file_reports_error` passes, `test_missing_required_section_reports_error` passes, `test_example_fixture_validates` still fails (fixture not built yet).

- [ ] **Step 5: Commit**

```bash
git add scripts/verify_sales_config.py tests/test_sales_config.py
git commit -m "feat: add verify_sales_config.py linter and fixture tests"
```

---

### Task 3: Example seller config fixture (the canonical reference)

This fixture doubles as the verifier's positive test case AND as worked examples that the `/sales init` skill and the README can point users at. Fictional seller: **"Lighthouse Analytics"** with two propositions.

**Files:**
- Create: `tests/fixtures/sales-config-example/.sales/identity.md`
- Create: `tests/fixtures/sales-config-example/.sales/icp.md`
- Create: `tests/fixtures/sales-config-example/.sales/pricing.md`
- Create: `tests/fixtures/sales-config-example/.sales/case-studies.md`
- Create: `tests/fixtures/sales-config-example/.sales/competitive.md`
- Create: `tests/fixtures/sales-config-example/.sales/objections.md`
- Create: `tests/fixtures/sales-config-example/.sales/propositions/onboarding-suite.md`
- Create: `tests/fixtures/sales-config-example/.sales/propositions/analytics-platform.md`

- [ ] **Step 1: Create `identity.md`**

```markdown
# Identity

## Company
**Legal name:** Lighthouse Analytics, Inc.
**DBA:** Lighthouse

## Senders
- Name: Avery Chen
  Title: Head of Growth
  Email: avery@lighthouse.example
  LinkedIn: https://www.linkedin.com/in/avery-chen-example

## Voice and Tone
**Adjectives:** direct, curious, evidence-driven.
We write the way a senior analyst would talk to a peer: specific, no hedging, no marketing fluff. Every claim should be backed by a number or a customer name.

## Signature
Avery Chen
Head of Growth, Lighthouse Analytics
avery@lighthouse.example • https://lighthouse.example

## Company Bio
Lighthouse Analytics helps mid-market SaaS teams turn raw product telemetry into onboarding interventions that lift activation. Founded in 2022, used by 80+ Series A–C companies. We sit between your warehouse and your CRM and trigger plays based on user behavior in the first 14 days.
```

- [ ] **Step 2: Create `icp.md`**

```markdown
# Ideal Customer Profile

## ICP Summary
Series A–C B2B SaaS companies (50–500 employees, $5M–$50M ARR) with self-serve or hybrid sales motions, a paying customer base of 500+ accounts, and an existing product analytics tool. Strongest fit is companies where activation rate is a board-level KPI and where the head of growth or VP product is the budget owner.

## Firmographic Criteria

| Criterion | Ideal Range | Why It Matters | Red Flag |
|---|---|---|---|
| ARR | $5M–$50M | Big enough to staff growth, small enough to move fast | <$2M ARR (no budget) |
| Employees | 50–500 | Past founder-led; not yet enterprise-procurement | 1000+ (long cycles) |
| Funding stage | Series A–C | Cash for growth bets | Bootstrapped no-budget |
| Geography | US, Canada, UK, EU | Time-zone overlap | APAC (currently underserved) |
| Industry | B2B SaaS | Our entire data model assumes SaaS | E-commerce, marketplaces |
| Customer base | 500+ accounts | Cohorts are statistically meaningful | <100 accounts (noise) |

## Pain Point Map
1. **Low activation** — new signups never get to first-value; CSMs spend hours on manual outreach
2. **Telemetry without action** — warehouses are full of events that no one triggers off
3. **Onboarding email rot** — sequences haven't been updated since launch

## Buyer Personas
**Persona: The Activation-Obsessed Head of Growth.** Owns activation rate as a board metric. Reads Lenny's Newsletter. Has Mixpanel or Amplitude. Frustrated that they can see the drop-off but can't act on it without engineering.
```

- [ ] **Step 3: Create `pricing.md`**

```markdown
# Pricing

## Tiers

| Tier | Price | Includes |
|---|---|---|
| Starter | $1,200 / month | Up to 25k MAUs, 3 plays, email + Slack channels |
| Growth | $3,500 / month | Up to 150k MAUs, unlimited plays, all channels, A/B testing |
| Enterprise | Custom (typically $60k–$150k ARR) | Unlimited MAUs, SSO, dedicated CSM, custom integrations |

## Deal Size Benchmarks
- Typical ACV: $42k
- Minimum viable deal: $14k (Starter annual)
- Enterprise threshold: $60k ARR

## Discount Rules
- Annual prepay: 15% off published list
- Multi-year (2+ years): additional 5%
- Discounts beyond 20% require Head of Growth approval

## Contract Terms
- Standard term: 12 months
- Renewal: auto-renew with 60-day opt-out
- Cancellation: pro-rata refund inside first 30 days
```

- [ ] **Step 4: Create `case-studies.md`**

```markdown
# Case Studies

## Plotly Studio (B2B Dev Tools, Series B)
### Customer
Plotly Studio — collaborative notebook platform, ~120 employees.
### Problem
38% of paid signups never completed the second core action; activation rate was the top board metric and was flat for 6 months.
### Solution
Deployed Lighthouse Onboarding Suite with 4 behavior-triggered plays inside the first 14 days.
### Metric
Activation lifted from 41% to 58% in 9 weeks. Now $0.42 saved per signup in CSM time.
### Quote
> "We finally have a closed loop between 'we see the drop-off' and 'we did something about it.'" — VP Product

## Crowdstack (Community SaaS, Series A)
### Customer
Crowdstack — community platform for B2B brands, ~75 employees.
### Problem
Onboarding emails hadn't been updated in 18 months and tested poorly against control.
### Solution
Lighthouse Analytics Platform identified the three highest-leverage activation events; the team rewrote sequences around them.
### Metric
Trial-to-paid conversion increased 22% (from 9.1% to 11.1%).
```

- [ ] **Step 5: Create `competitive.md`**

```markdown
# Competitive

## Positioning Statement
Lighthouse is the only product-led activation tool that triggers off your warehouse events without requiring engineering to ship a new SDK.

## Competitors

### Pendo
- **Their target:** Mid-market product teams who want guided tours and surveys
- **Their differentiator:** Mature in-app UI library
- **Our win story:** "Pendo shows you the funnel; we close it. Their plays live in the UI; ours live in the channels users actually open."
- **Our loss story:** Customers who want WYSIWYG tour-building and don't have a warehouse.
- **Displacement triggers:** Pendo renewal coming up; product team frustrated by inability to act on telemetry outside the app.

### Customer.io
- **Their target:** Lifecycle marketing teams
- **Their differentiator:** Best-in-class email composer
- **Our win story:** "Customer.io is great for marketing-led; we're built for product-led. We bind plays to product events, not to email lists."
- **Our loss story:** Customers whose primary need is broadcast marketing email.
- **Displacement triggers:** Marketing team trying to do activation work that should sit with product.
```

- [ ] **Step 6: Create `objections.md`**

```markdown
# Objection Playbook

## Top Objections

### "We already have Mixpanel/Amplitude."
**Underlying concern:** "Why pay for another tool that looks at the same events?"
**Response:** Mixpanel and Amplitude tell you what happened. Lighthouse triggers what happens next. We sit downstream of your warehouse and your analytics tool — we read the same events, but we act on them via email, Slack, and in-app.
**Evidence:** Plotly Studio case study — they kept Amplitude and added us for the action layer.

### "Our engineering team needs to ship an SDK."
**Underlying concern:** "This will take three months we don't have."
**Response:** No SDK. We read from your existing warehouse (Snowflake/BigQuery/Redshift) or your Segment stream. Standard install is 90 minutes.
**Evidence:** Crowdstack went live in 2 days.

### "We're not big enough for this."
**Underlying concern:** Budget or perceived complexity.
**Response:** Starter is $1,200/month and turns on in an afternoon. The math: if you save your CSM 5 hours a week of manual onboarding outreach, the tool pays for itself.

### "Can we just build this in our existing email tool?"
**Underlying concern:** Avoiding tool sprawl.
**Response:** You can; teams who try usually come back inside 6 months. The thing that's hard to build is the event-to-play binding logic, not the email send. We've built that part 80 times.
```

- [ ] **Step 7: Create `propositions/onboarding-suite.md`**

```markdown
# Onboarding Suite

## Name
Onboarding Suite

## Slug
onboarding-suite

## Value Prop
Turn product telemetry into behavior-triggered onboarding plays that lift activation 15–25% in the first 90 days.

## Target Persona
Activation-obsessed Head of Growth or VP Product at a Series A–C B2B SaaS company.

## Key Features
- Pre-built activation play library (12 plays out of the box)
- Trigger on any warehouse event or Segment stream
- Channels: email, Slack, in-app banner, webhook
- Built-in A/B testing per play
- Activation funnel report shipped to your inbox weekly

## Differentiators
- No SDK required — reads from warehouse, not your codebase
- Plays live as code, not as drag-and-drop UI; engineers can review in PR
- Closes the loop between Mixpanel/Amplitude and your email tool

## Ideal Use Cases
- Self-serve SaaS with flat activation rate
- Product team that has the data but can't act on it
- Replacing a hand-built Zapier-and-airtable rig

## Pricing Tier Reference
Starter and Growth tiers in `pricing.md`. Most onboarding-suite-only customers land on Growth ($3,500/month).

## Success Metrics
- Activation rate lift (primary)
- Trial-to-paid conversion rate
- CSM hours saved per signup

## Anti-Fit Signals
- No product analytics tool installed → too early
- Marketing-led GTM only → wrong buyer
- E-commerce or marketplace business → wrong data model
```

- [ ] **Step 8: Create `propositions/analytics-platform.md`**

```markdown
# Analytics Platform

## Name
Analytics Platform

## Slug
analytics-platform

## Value Prop
The activation analytics layer that tells you exactly which 3–5 product events predict paid conversion — and bakes that insight into a weekly executive scorecard.

## Target Persona
Head of Product or Head of Growth who needs a board-ready activation number and doesn't have a dedicated data analyst.

## Key Features
- Predictive event ranker (which events correlate with conversion)
- Weekly executive scorecard delivered by email
- Cohort comparison: this week vs last week vs same-week-last-quarter
- One-click export to Notion, Slack, Linear

## Differentiators
- Opinionated: tells you which 3 events to care about, not 300
- No dashboard-building required — comes preconfigured
- Built specifically for B2B SaaS activation, not generic product analytics

## Ideal Use Cases
- Pre-IPO or board-prep cycles where activation must become a tracked KPI
- Product teams without a data analyst
- Teams who tried Mixpanel and got lost in dashboards

## Pricing Tier Reference
Starter or Growth in `pricing.md`. Analytics-only customers most often start on Starter ($1,200/month).

## Success Metrics
- Time to a board-ready activation number (days)
- Number of activation events the team agrees to track
- Weekly scorecard open rate

## Anti-Fit Signals
- Team already has a senior data analyst → they'll build their own
- Less than 500 monthly active users → not enough signal
- Enterprise SaaS with custom event pipelines → use Onboarding Suite instead
```

- [ ] **Step 9: Run all verifier tests — all three should pass now**

Run: `pytest tests/test_sales_config.py -v`
Expected: 3 tests pass.

- [ ] **Step 10: Run the verifier directly on the fixture as a sanity check**

Run: `python scripts/verify_sales_config.py tests/fixtures/sales-config-example/.sales`
Expected: exit code 0, no output.

- [ ] **Step 11: Commit**

```bash
git add tests/fixtures/sales-config-example/
git commit -m "feat: add Lighthouse Analytics example .sales/ fixture"
```

---

### Task 4: Phase 0 verifier for SKILL.md files

Lints that each migrated skill's SKILL.md has a `## Phase 0: Load Seller Context` section and mentions each expected file path. Drives every Phase 4 / Phase 5 migration TDD-style.

**Files:**
- Create: `scripts/verify_skill_phase0.py`
- Create: `tests/test_skill_phase0.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_skill_phase0.py`:

```python
import subprocess
import sys
from pathlib import Path


VERIFY_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verify_skill_phase0.py"


def _run() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT)],
        capture_output=True,
        text=True,
    )


def test_phase0_verifier_runs() -> None:
    result = _run()
    # Before any skills are migrated, the verifier should report missing
    # Phase 0 sections; that is the expected starting state. We assert the
    # output mentions the contract so an engineer reading the failure knows
    # what to do.
    assert "Phase 0" in result.stdout + result.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skill_phase0.py -v`
Expected: FAIL — script does not exist.

- [ ] **Step 3: Implement the verifier**

Create `scripts/verify_skill_phase0.py`:

```python
"""Lint that each sales SKILL.md has a Phase 0: Load Seller Context block
mentioning the files the skill is required to load (per the design spec).

Usage: python scripts/verify_skill_phase0.py

Exits 0 if every skill in the contract passes, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


SKILL_CONTRACT: dict[str, list[str]] = {
    "skills/sales-contacts/SKILL.md": ["identity.md", "propositions/<slug>.md"],
    "skills/sales-qualify/SKILL.md": ["icp.md", "propositions/<slug>.md"],
    "skills/sales-outreach/SKILL.md": [
        "identity.md",
        "propositions/<slug>.md",
        "case-studies.md",
        "competitive.md",
    ],
    "skills/sales-followup/SKILL.md": ["identity.md", "propositions/<slug>.md"],
    "skills/sales-prep/SKILL.md": [
        "propositions/<slug>.md",
        "objections.md",
        "competitive.md",
    ],
    "skills/sales-proposal/SKILL.md": [
        "propositions/<slug>.md",
        "pricing.md",
        "case-studies.md",
        "identity.md",
    ],
    "skills/sales-objections/SKILL.md": [
        "objections.md",
        "competitive.md",
        "propositions/<slug>.md",
    ],
    "skills/sales-prospect/SKILL.md": [
        "identity.md",
        "icp.md",
        "pricing.md",
        "case-studies.md",
        "competitive.md",
        "objections.md",
        "propositions/<slug>.md",
    ],
    "skills/sales-report/SKILL.md": ["identity.md"],
    "skills/sales-report-pdf/SKILL.md": ["identity.md"],
}


PHASE0_HEADER = "## Phase 0: Load Seller Context"


def verify() -> list[str]:
    errors: list[str] = []
    for relpath, required_files in SKILL_CONTRACT.items():
        path = REPO_ROOT / relpath
        if not path.is_file():
            errors.append(f"{relpath}: file not found")
            continue
        text = path.read_text(encoding="utf-8")
        if PHASE0_HEADER not in text:
            errors.append(f"{relpath}: missing '{PHASE0_HEADER}' section")
            continue
        # Locate Phase 0 block: from its header to the next ## header or EOF.
        start = text.index(PHASE0_HEADER)
        rest = text[start + len(PHASE0_HEADER):]
        next_header = rest.find("\n## ")
        block = rest if next_header == -1 else rest[:next_header]
        for filename in required_files:
            if filename not in block:
                errors.append(f"{relpath}: Phase 0 must mention '{filename}'")
    return errors


def main() -> int:
    errors = verify()
    for err in errors:
        print(err)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test — it should pass now (verifier exists; output mentions "Phase 0")**

Run: `pytest tests/test_skill_phase0.py -v`
Expected: pass.

- [ ] **Step 5: Run the verifier directly — should report many failures (every skill missing Phase 0)**

Run: `python scripts/verify_skill_phase0.py; echo "exit=$?"`
Expected: ~10 lines like `skills/sales-contacts/SKILL.md: missing '## Phase 0: Load Seller Context' section`, exit code 1.

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_skill_phase0.py tests/test_skill_phase0.py
git commit -m "feat: add Phase 0 SKILL.md contract verifier"
```

---

## Phase 2: sales-init skill

The new skill is the user-facing way to populate `.sales/`. It's a single SKILL.md with seven distinct procedures (one per section) plus a top-level orchestrator and an optional `--from-url` seeding mode.

### Task 5: Scaffold sales-init/SKILL.md

**Files:**
- Create: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Create the skill scaffold**

```markdown
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

(filled in by Task 6)

## ICP Section

(filled in by Task 7)

## Proposition Section

(filled in by Task 8)

## Pricing Section

(filled in by Task 9)

## Case Studies Section

(filled in by Task 10)

## Competitive Section

(filled in by Task 11)

## Objections Section

(filled in by Task 12)

## Web Seeding (`--from-url`)

(filled in by Task 13)

---

## Quality Standards

- Every file written must validate against `python scripts/verify_sales_config.py`. If validation fails, fix and re-write before reporting success.
- Use the Write tool for new files; use Edit for partial updates.
- Mirror the structure of the fixture at `tests/fixtures/sales-config-example/.sales/` exactly — same H2 headers, same order.
- After writing each file, briefly confirm to the user what was written and how to regenerate it later.
```

- [ ] **Step 2: Verify the scaffold is valid markdown and visible to the skill runtime**

Run: `cat skills/sales-init/SKILL.md | head -5`
Expected: header line `# Seller Config Initializer` printed.

- [ ] **Step 3: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat: scaffold sales-init skill"
```

---

### Task 6: Identity section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Identity Section` placeholder**

Use Edit to replace `## Identity Section\n\n(filled in by Task 6)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add identity section procedure"
```

---

### Task 7: ICP section (port from sales-icp)

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## ICP Section` placeholder**

Use Edit to replace `## ICP Section\n\n(filled in by Task 7)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): port ICP-builder procedure into init"
```

---

### Task 8: Proposition section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Proposition Section` placeholder**

Use Edit to replace `## Proposition Section\n\n(filled in by Task 8)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add proposition section with loop"
```

---

### Task 9: Pricing section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Pricing Section` placeholder**

Use Edit to replace `## Pricing Section\n\n(filled in by Task 9)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add pricing section procedure"
```

---

### Task 10: Case studies section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Case Studies Section` placeholder**

Use Edit to replace `## Case Studies Section\n\n(filled in by Task 10)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add case studies section procedure"
```

---

### Task 11: Competitive section

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Competitive Section` placeholder**

Use Edit to replace `## Competitive Section\n\n(filled in by Task 11)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add competitive section procedure"
```

---

### Task 12: Objections section + per-section regeneration finalization

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Objections Section` placeholder**

Use Edit to replace `## Objections Section\n\n(filled in by Task 12)` with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add objections section procedure"
```

---

### Task 13: Web seeding (`--from-url`)

**Files:**
- Modify: `skills/sales-init/SKILL.md`

- [ ] **Step 1: Replace the `## Web Seeding (--from-url)` placeholder**

Use Edit to replace `## Web Seeding (\`--from-url\`)\n\n(filled in by Task 13)` with:

```markdown
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
```

- [ ] **Step 2: Run the verifier to ensure the example fixture is still valid (sanity check)**

Run: `python scripts/verify_sales_config.py tests/fixtures/sales-config-example/.sales`
Expected: exit code 0, no output.

- [ ] **Step 3: Commit**

```bash
git add skills/sales-init/SKILL.md
git commit -m "feat(sales-init): add --from-url web seeding procedure"
```

---

## Phase 3: Main orchestrator and sales-icp alias

### Task 14: Update sales/SKILL.md command grammar and routing

**Files:**
- Modify: `sales/SKILL.md`

- [ ] **Step 1: Replace the entire Command Reference table**

Use Edit to replace the existing Command Reference table (lines 7–22 in the current file) with:

```markdown
| Command | Description | Output |
|---------|-------------|--------|
| `/sales init [section]` | Scaffold/regenerate seller config in `./.sales/` | `.sales/*.md` |
| `/sales init --from-url=<url>` | Seed seller config from a corporate website | `.sales/*.md` |
| `/sales prospect <url> --proposition=<slug>` | Full prospect audit (5 parallel agents) | PROSPECT-ANALYSIS.md |
| `/sales quick <url>` | 60-second prospect snapshot (no seller config required) | Terminal output |
| `/sales research <url>` | Company research & firmographics (no seller config required) | COMPANY-RESEARCH.md |
| `/sales qualify <url> --proposition=<slug>` | Lead qualification (BANT/MEDDIC) against your ICP | LEAD-QUALIFICATION.md |
| `/sales contacts <url> --proposition=<slug>` | Decision maker identification | DECISION-MAKERS.md |
| `/sales outreach <prospect> --proposition=<slug>` | Cold outreach email sequence | OUTREACH-SEQUENCE.md |
| `/sales followup <prospect> --proposition=<slug>` | Follow-up email sequence | FOLLOWUP-SEQUENCE.md |
| `/sales prep <url> --proposition=<slug>` | Meeting preparation brief | MEETING-PREP.md |
| `/sales proposal <client> --proposition=<slug>` | Client proposal generator | CLIENT-PROPOSAL.md |
| `/sales objections <topic> --proposition=<slug>` | Objection handling playbook | OBJECTION-PLAYBOOK.md |
| `/sales icp [description]` | Back-compat alias → `/sales init icp` | `.sales/icp.md` |
| `/sales competitors <url>` | Competitive intelligence | COMPETITIVE-INTEL.md |
| `/sales report` | Sales pipeline report (Markdown) | SALES-REPORT.md |
| `/sales report-pdf` | Sales pipeline report (PDF) | SALES-REPORT-*.pdf |
```

- [ ] **Step 2: Add a new "Seller Config" section before "Routing Logic"**

Use Edit to insert this block immediately before the line `## Routing Logic`:

```markdown
## Seller Config (`.sales/`)

Every command marked with `--proposition=<slug>` in the table above requires a project-local seller config at `./.sales/`. If that folder is missing, the skill must error with:

> "No seller config found. Run `/sales init` to set one up."

If `--proposition=<slug>` is missing or the slug is not present in `./.sales/propositions/`, the skill must error with one of:

> "Which proposition? Available: <slug list>. Re-run with `--proposition=<slug>`."
> "Proposition '<slug>' not found in `.sales/propositions/`. Available: <slug list>."

Commands NOT requiring seller config: `/sales init`, `/sales quick`, `/sales research`, `/sales competitors`, `/sales icp` (which is itself the alias to `/sales init icp`). The `report` and `report-pdf` commands require `.sales/identity.md` for branding but do not require a `--proposition` flag.

The example fixture at `tests/fixtures/sales-config-example/.sales/` shows the exact shape of every file. Skills must reference it when uncertain.

---

```

- [ ] **Step 3: Update the Routing Logic section**

Use Edit to replace the existing routing block that begins `### Full Prospect Analysis` and ends before `## Business Context Detection`. Replace it with this updated version that mentions the new flag:

```markdown
### Seller Config Setup (`/sales init`)
Route to `skills/sales-init/SKILL.md`. Handles full setup, per-section regeneration, and `--from-url` seeding.

### Full Prospect Analysis (`/sales prospect <url> --proposition=<slug>`)
This is the flagship command. After loading seller context (all six base files plus the selected proposition), it launches **5 parallel subagents** to analyze a prospect simultaneously, passing the loaded seller context as part of the discovery briefing to each:

1. **sales-company** agent → Company research, firmographics, growth signals, tech stack
2. **sales-contacts** agent → Decision maker identification, org mapping, personalization anchors
3. **sales-opportunity** agent → Lead qualification, pain points, budget signals, buying timeline
4. **sales-competitive** agent → Current solutions, switching costs, competitive positioning
5. **sales-strategy** agent → Outreach strategy, messaging, channel recommendation, objection prep

The prospect score uses the weights defined in `.sales/icp.md`'s scoring rubric, not generic defaults.

**Prospect Scoring Methodology (Prospect Score 0-100):**
(Unchanged — see below.)

### Quick Snapshot (`/sales quick <url>`)
Unchanged from prior behavior. Seller-agnostic by design.

### Individual Commands
For all other commands, route to the corresponding sub-skill in `skills/sales-<command>/SKILL.md`. Each sub-skill is responsible for enforcing its own `.sales/` and `--proposition` requirements at Phase 0 of its procedure.
```

- [ ] **Step 4: Verify file is still well-formed**

Run: `grep -c '^##' sales/SKILL.md`
Expected: a positive integer (multiple H2 headers).

- [ ] **Step 5: Commit**

```bash
git add sales/SKILL.md
git commit -m "feat(orchestrator): update command grammar with --proposition and .sales/"
```

---

### Task 15: Rewrite sales-icp as a delegating alias

**Files:**
- Modify: `skills/sales-icp/SKILL.md`

- [ ] **Step 1: Replace the entire file**

Use Write to overwrite `skills/sales-icp/SKILL.md`:

```markdown
# Ideal Customer Profile Builder (alias)

## Metadata
- **Title:** Ideal Customer Profile Builder
- **Invocation:** `/sales icp [description]` — back-compat alias
- **Output:** `./.sales/icp.md`

---

This skill is a back-compatibility alias retained so that `/sales icp <description>` from prior documentation continues to work.

**Behavior:** Delegate to `/sales init icp [description]` and stop. Do not produce a standalone `IDEAL-CUSTOMER-PROFILE.md` in the working directory — the canonical location is now `./.sales/icp.md`.

If `./.sales/` does not exist, `/sales init icp` will create it (along with the `.sales/icp.md` file). No other files are touched.

For full setup of the seller config, point the user at `/sales init`.
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-icp/SKILL.md
git commit -m "refactor(sales-icp): convert to delegating alias to /sales init icp"
```

---

## Phase 4: Migrate skills that consume seller context

Each task in this phase follows the same TDD shape:

1. Run `python scripts/verify_skill_phase0.py` and confirm the skill is in the failure list.
2. Edit the skill's SKILL.md to add a `## Phase 0: Load Seller Context` section immediately after the opening prose (before the first existing `## Phase` or `## When This Skill Is Invoked`).
3. Update the downstream procedure to reference the loaded seller context.
4. Add the output header block requirement (Seller / Proposition / ICP / Generated) to the skill's Output Format section.
5. Run `python scripts/verify_skill_phase0.py` and confirm the skill is no longer in the failure list.
6. Commit.

Use the Phase 0 template defined at the top of this plan, with the per-skill file list from the table below.

### Task 16: sales-contacts

**Files:**
- Modify: `skills/sales-contacts/SKILL.md`

- [ ] **Step 1: Run the verifier and confirm sales-contacts is failing**

Run: `python scripts/verify_skill_phase0.py | grep sales-contacts`
Expected: `skills/sales-contacts/SKILL.md: missing '## Phase 0: Load Seller Context' section`

- [ ] **Step 2: Insert Phase 0 immediately after the file's opening prose**

Phase 0 files for this skill: `identity.md`, `propositions/<slug>.md`.

Use the template at the top of this plan. The "Files to load:" block becomes:

```markdown
**Files to load:**
- `.sales/identity.md` — seller name and primary sender persona; used to scope which decision-maker titles map to which sender for the outreach hand-off
- `.sales/propositions/<slug>.md` — proposition's Target Persona; used to bias the decision-maker search toward titles that buy THIS proposition
```

- [ ] **Step 3: Update the downstream procedure to reference seller context**

Add this paragraph near the start of the existing decision-maker identification procedure:

```markdown
**Use seller context.** When ranking decision makers, score "Title Match" against the proposition's Target Persona from `.sales/propositions/<slug>.md` rather than a generic ICP. Surface the matching persona name in the output so the salesperson can see why each contact was ranked.
```

- [ ] **Step 4: Update the output file header**

In the Output Format section, ensure the top of `DECISION-MAKERS.md` includes:

```markdown
Seller: <identity.company>
Proposition: <slug> — <name>
ICP: .sales/icp.md
Generated: <date>
```

- [ ] **Step 5: Run the verifier and confirm sales-contacts now passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-contacts || echo "OK"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add skills/sales-contacts/SKILL.md
git commit -m "feat(sales-contacts): consume seller context (Phase 0)"
```

---

### Task 17: sales-qualify

**Files:**
- Modify: `skills/sales-qualify/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-qualify`
Expected: failure line.

- [ ] **Step 2: Insert Phase 0**

Phase 0 files for this skill: `icp.md`, `propositions/<slug>.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/icp.md` — global ICP including scoring rubric; the qualification procedure uses these weights, not generic defaults
- `.sales/propositions/<slug>.md` — proposition's Ideal Use Cases and Anti-Fit Signals; used to refine the BANT/MEDDIC qualification beyond the global ICP
```

- [ ] **Step 3: Update the scoring procedure to use the loaded ICP rubric**

Add a paragraph near the top of the qualification procedure:

```markdown
**Use seller's ICP rubric.** The 100-point qualification rubric uses the weights and grade bands defined in `.sales/icp.md` (under `## ICP Scoring Rubric`). Do not invent generic weights. Augment with the proposition's Anti-Fit Signals to flag disqualifiers specific to this proposition.
```

- [ ] **Step 4: Update output header in `LEAD-QUALIFICATION.md`**

Same header template as Task 16 Step 4.

- [ ] **Step 5: Confirm verifier passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-qualify || echo "OK"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add skills/sales-qualify/SKILL.md
git commit -m "feat(sales-qualify): consume seller context (Phase 0)"
```

---

### Task 18: sales-outreach

**Files:**
- Modify: `skills/sales-outreach/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-outreach`
Expected: failure line.

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `identity.md`, `propositions/<slug>.md`, `case-studies.md`, `competitive.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/identity.md` — Senders block (use the configured sender persona for from-name, signature, and LinkedIn handle); Voice and Tone (every email must match these adjectives)
- `.sales/propositions/<slug>.md` — Value Prop, Key Features, Differentiators (these become the body of the emails)
- `.sales/case-studies.md` — at least one case study must be cited verbatim in the sequence; pick the one whose industry best matches the prospect
- `.sales/competitive.md` — if the prospect uses a known competitor, lead with the displacement trigger and our win story
```

- [ ] **Step 3: Update the email-generation procedure**

Add this paragraph at the top of the email-generation section:

```markdown
**Use seller context everywhere.** No email may contain a generic value claim. Each email must (a) be signed by the configured Sender, (b) match the configured Voice and Tone adjectives, (c) reference at least one specific item from the selected proposition (a feature, differentiator, or success metric), and (d) cite a real case study customer name from `.sales/case-studies.md` when claiming results. Generic claims ("companies like yours see X%") are forbidden — use the specific named customer instead.
```

- [ ] **Step 4: Update output header in `OUTREACH-SEQUENCE.md`**

Same header template.

- [ ] **Step 5: Confirm verifier passes**

Run: `python scripts/verify_skill_phase0.py | grep sales-outreach || echo "OK"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add skills/sales-outreach/SKILL.md
git commit -m "feat(sales-outreach): consume seller context (Phase 0)"
```

---

### Task 19: sales-followup

**Files:**
- Modify: `skills/sales-followup/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-followup`

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `identity.md`, `propositions/<slug>.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/identity.md` — Sender + Voice and Tone for follow-up emails
- `.sales/propositions/<slug>.md` — proposition details to reference in follow-ups
```

- [ ] **Step 3: Update procedure**

Add:

```markdown
**Use seller context.** Every follow-up email is signed by the configured Sender, matches the Voice and Tone adjectives, and references at least one specific item from the proposition that builds on (rather than repeats) the initial outreach.
```

- [ ] **Step 4: Update output header in `FOLLOWUP-SEQUENCE.md`**

- [ ] **Step 5: Confirm verifier passes; commit**

```bash
git add skills/sales-followup/SKILL.md
git commit -m "feat(sales-followup): consume seller context (Phase 0)"
```

---

### Task 20: sales-prep

**Files:**
- Modify: `skills/sales-prep/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-prep`

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `propositions/<slug>.md`, `objections.md`, `competitive.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/propositions/<slug>.md` — proposition details, ideal use cases, anti-fit signals; the prep brief must anticipate which proposition aspects will land and which will not
- `.sales/objections.md` — pre-loaded responses for objections the prospect is likely to raise
- `.sales/competitive.md` — if the prospect uses a known competitor, surface our win story and displacement triggers in the prep brief
```

- [ ] **Step 3: Update procedure**

Add to the prep brief structure:

```markdown
**Use seller context.** The "Anticipated Objections" section of the prep brief pulls verbatim from `.sales/objections.md` rather than generic objection lists. The "Competitive Risks" section pulls from `.sales/competitive.md`. The "Recommended Pitch Angle" must call out which specific Ideal Use Case from `.sales/propositions/<slug>.md` this prospect aligns with (or note that they do not align with any, which is itself important information).
```

- [ ] **Step 4: Update output header in `MEETING-PREP.md`**

- [ ] **Step 5: Confirm verifier; commit**

```bash
git add skills/sales-prep/SKILL.md
git commit -m "feat(sales-prep): consume seller context (Phase 0)"
```

---

### Task 21: sales-proposal

**Files:**
- Modify: `skills/sales-proposal/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-proposal`

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `propositions/<slug>.md`, `pricing.md`, `case-studies.md`, `identity.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/propositions/<slug>.md` — proposition Name, Value Prop, Key Features, Differentiators, Success Metrics. The proposal's "Solution" and "Why Us" sections are built directly from these.
- `.sales/pricing.md` — Tiers and Discount Rules. The proposal's "Investment" section uses the tier referenced by the proposition.
- `.sales/case-studies.md` — Select 1–2 case studies whose industry/stage most closely match the client; embed them in the proposal.
- `.sales/identity.md` — Company Bio for the "About Us" section; Sender persona for the cover page.
```

- [ ] **Step 3: Update procedure**

Add to the proposal-generation procedure:

```markdown
**Use seller context.** No section of the proposal may contain a placeholder ("Your Company") or a generic value claim. Pull the proposition's exact wording for Value Prop and Differentiators; pull the matching tier verbatim from `.sales/pricing.md`; embed at least one named case study with its quantified result. The cover page lists the configured Sender as the proposal author.
```

- [ ] **Step 4: Update output header in `CLIENT-PROPOSAL.md`**

- [ ] **Step 5: Confirm verifier; commit**

```bash
git add skills/sales-proposal/SKILL.md
git commit -m "feat(sales-proposal): consume seller context (Phase 0)"
```

---

### Task 22: sales-objections

**Files:**
- Modify: `skills/sales-objections/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-objections`

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `objections.md`, `competitive.md`, `propositions/<slug>.md`.

Files-to-load block:

```markdown
**Files to load:**
- `.sales/objections.md` — seed objection list; the playbook generated for the prospect must build ON this list, not duplicate it
- `.sales/competitive.md` — competitive context for any "Why not <competitor>?" objections
- `.sales/propositions/<slug>.md` — Anti-Fit Signals; if any signal applies to the prospect, surface it as a likely objection
```

- [ ] **Step 3: Update procedure**

Add:

```markdown
**Use seller context.** When generating the prospect-specific objection playbook, prepend the pre-validated responses from `.sales/objections.md` (they have proven evidence behind them). Only add new objections that are specific to this prospect's situation and that are not already covered by the seller's standing list.
```

- [ ] **Step 4: Update output header in `OBJECTION-PLAYBOOK.md`**

- [ ] **Step 5: Confirm verifier; commit**

```bash
git add skills/sales-objections/SKILL.md
git commit -m "feat(sales-objections): consume seller context (Phase 0)"
```

---

### Task 23: sales-prospect (orchestrator that fans out to agents)

**Files:**
- Modify: `skills/sales-prospect/SKILL.md`

- [ ] **Step 1: Confirm verifier failure**

Run: `python scripts/verify_skill_phase0.py | grep sales-prospect`

- [ ] **Step 2: Insert Phase 0**

Phase 0 files: `identity.md`, `icp.md`, `pricing.md`, `case-studies.md`, `competitive.md`, `objections.md`, `propositions/<slug>.md`.

Files-to-load block:

```markdown
**Files to load (all six base files plus the selected proposition):**
- `.sales/identity.md`
- `.sales/icp.md`
- `.sales/pricing.md`
- `.sales/case-studies.md`
- `.sales/competitive.md`
- `.sales/objections.md`
- `.sales/propositions/<slug>.md`

**Pass the loaded seller context to every subagent in the discovery briefing.** Subagents do not re-read these files themselves — they receive the context inline. See `agents/` for the consumption contract.
```

- [ ] **Step 3: Update the orchestrator's subagent dispatch**

Add to the subagent-dispatch procedure:

```markdown
**Briefing structure.** When dispatching each of the 5 subagents, include in the briefing:

1. The prospect URL and any pre-fetched page content
2. A `<seller_context>` block containing the full content of each file loaded in Phase 0 (relevant to that subagent — see per-agent map below)
3. The proposition slug and a one-paragraph summary

Per-agent context map:
- sales-company → ICP (for fit scoring)
- sales-contacts → identity.md (sender match), proposition (target persona)
- sales-opportunity → ICP (scoring rubric), proposition (Ideal Use Cases / Anti-Fit Signals)
- sales-competitive → competitive.md, proposition (Differentiators)
- sales-strategy → identity (voice/tone), proposition, case-studies, objections, competitive

The final PROSPECT-ANALYSIS.md aggregates all five subagent outputs and uses the weights from `.sales/icp.md`'s scoring rubric to compute the composite Prospect Score.
```

- [ ] **Step 4: Update output header in `PROSPECT-ANALYSIS.md`**

- [ ] **Step 5: Confirm verifier; commit**

```bash
git add skills/sales-prospect/SKILL.md
git commit -m "feat(sales-prospect): load seller context and pass to subagents"
```

---

### Task 24: sales-competitors (optional consumption)

**Files:**
- Modify: `skills/sales-competitors/SKILL.md`

This skill does NOT appear in `SKILL_CONTRACT` (the verifier expects no Phase 0). Instead, it has an OPTIONAL pickup: if `.sales/competitive.md` exists, enrich the output with the seller's positioning.

- [ ] **Step 1: Add an optional pickup section**

Add immediately after the opening prose:

```markdown
## Optional Seller Context

If `.sales/competitive.md` exists in the working directory, read it and incorporate the seller's `## Positioning Statement` and `## Competitors` entries into the output. Where a competitor in the seller's list matches a competitor surfaced by this skill's research, append the seller's `Our win story` and `Displacement triggers` to that competitor's profile in the output.

If `.sales/competitive.md` does not exist, proceed as before; no error.
```

- [ ] **Step 2: Commit**

```bash
git add skills/sales-competitors/SKILL.md
git commit -m "feat(sales-competitors): optionally consume .sales/competitive.md"
```

---

### Task 25: sales-report and sales-report-pdf

Both report skills hard-require `.sales/identity.md` for branding but do not take a `--proposition`. They aggregate across all proposition outputs found in the project.

**Files:**
- Modify: `skills/sales-report/SKILL.md`
- Modify: `skills/sales-report-pdf/SKILL.md`

- [ ] **Step 1: Insert Phase 0 in sales-report/SKILL.md**

The Phase 0 template is the same as the top of the plan, but adjusted: this skill takes no `--proposition` flag, only requires `.sales/identity.md`. The Phase 0 block becomes:

```markdown
## Phase 0: Load Seller Context

**Requires `.sales/` (project-local seller config).** If missing, error: `"No seller config found. Run /sales init to set one up."`

This skill does NOT take a `--proposition` flag. It aggregates across all proposition outputs found in the project's working directory.

**Files to load:**
- `.sales/identity.md` — used for branding the report header (company name and bio)

Every generated report includes the configured seller's name and bio at the top.
```

- [ ] **Step 2: Update sales-report procedure to include identity in the report header**

Add a note in the procedure: `The report header always starts with: "Pipeline Report for <identity.company>".`

- [ ] **Step 3: Insert Phase 0 in sales-report-pdf/SKILL.md (same template)**

- [ ] **Step 4: Update sales-report-pdf procedure**

Add: `The cover page uses the configured seller's name. The PDF's footer includes the company name on every page.`

- [ ] **Step 5: Confirm verifier passes for both skills**

Run: `python scripts/verify_skill_phase0.py | grep -E 'sales-report(-pdf)?' || echo "OK"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add skills/sales-report/SKILL.md skills/sales-report-pdf/SKILL.md
git commit -m "feat(sales-report*): consume identity for report branding (Phase 0)"
```

---

## Phase 5: Agents (subagents of `/sales prospect`)

### Task 26: Update all five agents to consume orchestrator-provided seller context

**Files:**
- Modify: `agents/sales-company.md`
- Modify: `agents/sales-contacts.md`
- Modify: `agents/sales-opportunity.md`
- Modify: `agents/sales-competitive.md`
- Modify: `agents/sales-strategy.md`

Agents do not load `.sales/` themselves. They receive a `<seller_context>` briefing from the orchestrator (per Task 23). This task adds a "Reading the Briefing" section to each agent so they know to use that context.

- [ ] **Step 1: Add a "Reading the Briefing" section near the top of each agent file**

For each of the five agent files, insert this block immediately after the agent's opening role description (typically the first paragraph):

```markdown
## Reading the Briefing

You are dispatched by `/sales prospect` as a subagent. Your briefing from the orchestrator includes a `<seller_context>` block with the contents of relevant `.sales/` files for this run. Do NOT re-read those files yourself.

Use the seller context as follows:

(per-agent guidance — see below)
```

Per-agent "use the seller context as follows" text:

- **sales-company:** "Score the prospect's Company Fit against the criteria in the seller's ICP (`.sales/icp.md`), not against generic ranges. The size, industry, growth, tech-sophistication, and budget sub-scores must reference the seller's ICP weights."
- **sales-contacts:** "Rank decision makers by their match to the proposition's Target Persona (from the seller_context proposition file). Surface in the output which Sender persona from `identity.md` should own the outreach hand-off."
- **sales-opportunity:** "Use the seller's ICP scoring rubric. Augment qualification with the proposition's Ideal Use Cases and Anti-Fit Signals — if any anti-fit signal applies, surface it as a disqualifier."
- **sales-competitive:** "When the prospect uses a known competitor that appears in `competitive.md`, surface the seller's Win Story and Displacement Triggers for that competitor."
- **sales-strategy:** "The recommended outreach plan must be signed by the configured Sender from `identity.md`, match the configured Voice and Tone, and lead with the proposition's Value Prop. Cite at least one case study from `case-studies.md` whose industry matches the prospect."

- [ ] **Step 2: Verify each agent file still parses as markdown (no broken H1/H2 structure)**

Run: `for f in agents/*.md; do echo "=== $f"; head -3 "$f"; done`
Expected: each file's header line printed cleanly.

- [ ] **Step 3: Commit**

```bash
git add agents/*.md
git commit -m "feat(agents): consume seller context from orchestrator briefing"
```

---

## Phase 6: Documentation and end-to-end verification

### Task 27: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current README to find the command table and quickstart**

Run: `grep -n '## \|/sales' README.md | head -40`

- [ ] **Step 2: Update the README command list**

Replace any command table in README.md to match the new grammar from Task 14 Step 1 (the Command Reference table). Use Edit for each table row that has changed.

- [ ] **Step 3: Add a new Quickstart section**

Insert immediately after the README's introductory paragraph, before any "Installation" or "Usage" section:

```markdown
## Quickstart

```bash
# 1. Scaffold your seller config (interactive)
/sales init

# Optional: seed from your corporate website
/sales init --from-url=https://yourcompany.example

# 2. Run a full prospect analysis against one of your propositions
/sales prospect https://prospect.example --proposition=<your-slug>

# 3. Generate cold outreach for the prospect
/sales outreach https://prospect.example --proposition=<your-slug>
```

The `--proposition=<slug>` flag is required for any command that personalizes output to a specific product or service in your portfolio. List available propositions with `ls .sales/propositions/`.

A complete worked example lives at [`tests/fixtures/sales-config-example/.sales/`](tests/fixtures/sales-config-example/.sales) — a fictional company called "Lighthouse Analytics" with two propositions. Use it as a reference when building your own.
```

- [ ] **Step 4: Retire the `IDEAL-CUSTOMER-PROFILE.md` mention**

Search for `IDEAL-CUSTOMER-PROFILE.md` in README.md and replace any reference with `.sales/icp.md`.

Run: `grep -n IDEAL-CUSTOMER-PROFILE README.md`
Expected after edits: no matches.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: update README for /sales init and seller config quickstart"
```

---

### Task 28: End-to-end verification

This is a manual verification task that runs the verifier suite and exercises the new flow end-to-end. It produces no code; it produces a confidence signal.

- [ ] **Step 1: Run the full verifier suite**

Run: `pytest tests/ -v && python scripts/verify_skill_phase0.py && python scripts/verify_sales_config.py tests/fixtures/sales-config-example/.sales`
Expected: all tests pass, both Python scripts exit 0.

- [ ] **Step 2: Exercise `/sales init` in a scratch directory**

```bash
mkdir -p /tmp/sales-init-smoketest && cd /tmp/sales-init-smoketest
# In Claude Code, run: /sales init
# Step through every section. Add at least one proposition.
# Verify that .sales/ is created with all required files.
python /Users/boukevlierhuis/github/ai-sales-team-claude/scripts/verify_sales_config.py ./.sales
```
Expected: exit code 0. No errors printed.

- [ ] **Step 3: Exercise `/sales init --from-url=...` against a known site**

```bash
mkdir -p /tmp/sales-init-fromurl && cd /tmp/sales-init-fromurl
# In Claude Code, run: /sales init --from-url=https://stripe.com
# Confirm that the init prompts present extracted candidate drafts (not blank forms) for at least: identity, propositions, pricing.
```
Expected: visible pre-filled drafts appear in the prompts. Sections that the site does not cover (e.g., objections) fall back to blank questions.

- [ ] **Step 4: Exercise a seller-required skill against the example fixture**

```bash
cd /Users/boukevlierhuis/github/ai-sales-team-claude/tests/fixtures/sales-config-example
# In Claude Code, run: /sales outreach https://example.com --proposition=onboarding-suite
# Inspect the generated OUTREACH-SEQUENCE.md:
#   - Header includes "Seller: Lighthouse Analytics, Inc." and "Proposition: onboarding-suite — Onboarding Suite"
#   - At least one email is signed by "Avery Chen, Head of Growth"
#   - At least one email references "Plotly Studio" or "Crowdstack" (from case-studies.md)
```
Expected: every check passes.

- [ ] **Step 5: Exercise the missing-config error path**

```bash
mkdir -p /tmp/sales-no-config && cd /tmp/sales-no-config
# In Claude Code, run: /sales outreach https://example.com --proposition=onboarding-suite
# Verify the error message: "No seller config found. Run /sales init to set one up."
```
Expected: the exact error message appears.

- [ ] **Step 6: Exercise the missing-proposition error path**

```bash
cd /Users/boukevlierhuis/github/ai-sales-team-claude/tests/fixtures/sales-config-example
# In Claude Code, run: /sales outreach https://example.com
# Verify the error: "Which proposition? Available: analytics-platform, onboarding-suite. Re-run with --proposition=<slug>."
```
Expected: the listed propositions appear in alphabetical order.

- [ ] **Step 7: Final commit (no code changes; this captures completion)**

If any small fixes were needed during verification, commit them. Otherwise, mark this plan complete via:

```bash
git log --oneline -30
```

Expected: a clean linear history of feature commits, ending with the README update and any verification fixes.

---

## Cross-Task Notes

- **Commit style.** Use conventional-commit prefixes (`feat:`, `refactor:`, `docs:`, `chore:`). One logical change per commit. The skill names go in the scope when relevant (e.g., `feat(sales-outreach): ...`).
- **TDD where it bites.** Every Python addition (verifier scripts) is preceded by a failing pytest assertion. Every SKILL.md migration is preceded by a failing `verify_skill_phase0.py` run. Markdown content edits inside the new init skill do not have automated tests beyond the verifier — manual review during Task 28 catches their correctness.
- **No backwards-compat detours.** The legacy `IDEAL-CUSTOMER-PROFILE.md` top-level file is gone after this plan ships. Any user with an existing one can copy it into `.sales/icp.md` by hand (or by re-running `/sales init icp`).
- **YAGNI guardrails.** Do not add: a YAML manifest in `.sales/`, a shared Python loader script that skills shell out to, walk-up directory discovery, user-global config, multi-seller mode, automatic proposition selection. All explicitly excluded by the spec.
