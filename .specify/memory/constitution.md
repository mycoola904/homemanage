<!--
Sync Impact Report:
- Version: 1.0.1 -> 1.0.2
- Modified Principles: III. Lean Dependencies & Small Surface Area; IV. Server-Driven UI & Template Safety; V. AI Accountability & Guardrails
- Added Sections: None
- Removed Sections: None
- Templates Updated:
  - .specify/templates/plan-template.md ✅ (alignment verified, no edits needed)
  - .specify/templates/spec-template.md ✅ (alignment verified, no edits needed)
  - .specify/templates/tasks-template.md ✅ (alignment verified, no edits needed)
- Follow-ups: None
-->
# HomeManage Constitution

## Core Principles

### I. Spec-First Delivery
Every change traces back to an approved `/speckit.spec`, `/speckit.plan`, and `/speckit.tasks` artifact before code is written. Pull requests that skip a referenced spec, plan, or task list are rejected. If the spec drifts, halt implementation and revise the document first. Tests must be written to fail against the spec scenario prior to implementing the fix or feature.
Clarification: Implementation can iterate as long as it stays within the documented acceptance criteria; spec drift—any change to requirements, scope, or externally observable behavior—requires updating the spec before coding resumes.

### II. Deterministic Correctness
Schema changes ship with tested migrations, repeatable data fixtures, and idempotent backfills. Every PR must demonstrate that the full automated test suite runs (tool-agnostic), migrations apply cleanly from a fresh database, and there are no uncommitted model or migration diffs. Business logic avoids unseeded randomness, clock-based behavior, or hidden global state; when such inputs are unavoidable they are explicitly seeded and logged. HTMX endpoints must behave as pure functions of request data and persisted state so swaps remain predictable. Deterministic proof first: prefer failing automated tests, but reproducible scenarios (e.g., captured template renders or HTMX exchanges) are acceptable when tests are impractical.

### III. Lean Dependencies & Small Surface Area
Prefer the Python standard library, Django, and existing utilities; “dependencies” includes runtime packages, managed services, and infrastructure components. Adding any new dependency demands a written justification, blast-radius assessment, and removal plan documented in the PR description or the project decisions log. Background workers, caches, or queues stay out until a spec proves necessity. Developer-only tooling is allowed when it measurably reduces overall complexity and never leaks into runtime paths. When alternatives exist, pick the simplest reversible solution that keeps the dependency graph tiny.

### IV. Server-Driven UI & Template Safety
All UX state originates on the server, while non-authoritative client-side hints (e.g., loading indicators or focus nudges) may provide temporary guidance. HTMX swaps only update declared containers and must not remove the element that triggers the request unless the implementation plan explicitly specifies and justifies the removal. CSS or class changes are blocked until `npm run dev` (Tailwind/DaisyUI) is confirmed live in the terminal. Django templates obey single-line `{% %}` and `{# #}` rules; conditional classes are computed in the view or a single-line `{% with %}` block to avoid parser failures.

### V. AI Accountability & Guardrails
Non-trivial AI-generated logic, templates, schema changes, or architectural decisions must cite the spec paragraph implemented and link to the prompt/response that produced them. Attribution records live in the relevant spec or, for design decisions, in the project decisions log; trivial edits (formatting, comments, typos) are exempt. Human reviewers verify AI output against Principles I–IV before merge. AI agents may not relax template constraints, introduce dependencies, or paper over watcher issues; any uncertainty is recorded as a TODO or open question inside the relevant doc.

## Stack & Determinism Constraints

- Backend: Python 3.11+, Django, server-rendered templates, and HTMX partial responses.
- Frontend styling: Tailwind CSS + DaisyUI compiled by the Node watcher; no SPA frameworks or client-side state stores.
- Database: SQLite for local development; production database engine TBD but must support transactional integrity and deterministic ordering.
- Environments must support repeatable migrations (`manage.py migrate --check`) and fixture loads. Data seeding scripts live in Django migrations or dedicated management commands.
- Observability: structured logging via Django's logging settings; third-party APM or telemetry requires spec approval due to Principle III.

## Workflow & Quality Gates

1. `/speckit.spec` -> `/speckit.plan` -> `/speckit.tasks` outputs are mandatory and must be linked from the branch description before implementation begins.
2. The plan's Constitution Check documents coverage for spec scenarios, migration strategy, dependency impact, and watcher confirmation steps.
3. Each HTMX endpoint defines its target IDs, failure states, and swap type inside the plan prior to coding.
4. PR descriptions include spec links, migration summaries, deterministic test evidence, and the IDs of AI prompts used.
5. CSS/template regressions require attaching watcher logs or screenshots proving the Tailwind watcher is running before code review.

### Assumptions & Open Questions

- Production database selection (likely PostgreSQL) needs confirmation before the first deployment.
- Observability stack (e.g., OpenTelemetry vs. ELK) remains undecided; decision required before adding external services.
- AI prompt retention location and duration must be defined to enforce Principle V record-keeping.

## Governance

- This constitution supersedes ad-hoc preferences; when conflicts arise, default to these principles.
- Amendments require an RFC in `docs/`, updates to this file, and validation that plan/spec/tasks templates reflect the new rules.
- Versioning: MAJOR for removing/redefining principles, MINOR for new principles/sections or stricter requirements, PATCH for clarifications.
- Compliance reviews occur at kickoff, pre-merge, and release retro. Missing specs, watcher evidence, or AI prompt logs block release until resolved.

**Version**: 1.0.2 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-06
