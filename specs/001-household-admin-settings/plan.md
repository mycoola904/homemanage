# Implementation Plan: Household Admin Settings

**Branch**: `001-household-admin-settings` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-household-admin-settings/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a server-driven Settings workflow for global administrators (MVP: Django superusers) to create households, create user login accounts with direct password set, and manage household memberships. Navigation must be authentication-aware (show Login only when unauthenticated; hide modules including Finance until authenticated), with deterministic validation and HTMX-safe partial updates that preserve stable containers.

## Technical Context

**Language/Version**: Python 3.11+, Django 6.x templates + HTMX  
**Primary Dependencies**: Django auth, Django ModelForms, HTMX, Tailwind CSS + DaisyUI (existing)  
**Storage**: SQLite for local/tests (`core.settings_test`), production engine unchanged  
**Testing**: Django test runner (`python manage.py test`), existing app tests in `financial/tests/` and feature-focused additions  
**Target Platform**: Server-rendered web app (Windows/Linux dev), browser clients
**Project Type**: Django web application (server-driven UI)  
**Performance Goals**: Admin CRUD interactions complete within success criteria (`<=90s` user create flow), no regression to existing household/account routing latency  
**Constraints**: No new runtime dependencies; deterministic migrations/fixtures; HTMX swaps must keep trigger/stable containers; template tag single-line safety rules  
**Scale/Scope**: Local single-operator admin workflow; global admin managing multiple households and memberships

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: Covered by `spec.md` user stories/FR-001..FR-022 and clarifications. Pre-implementation failing tests to add: admin-settings access control, nav auth visibility, household creation validation, user create-with-memberships, no-household blocking, membership add/remove idempotency.
- [x] **Deterministic Data Plan**: Add deterministic migration(s) for any new admin-specific fields/constraints only if needed; rely on existing `Household`/`HouseholdMember` schema where possible. Include reversible migrations, fixture updates with fixed identifiers/order, and rollback via migration reverse.
- [x] **Dependency Discipline**: No new runtime dependencies planned; use Django auth/forms/permissions and existing HTMX/Tailwind stack.
- [x] **Template & Watcher Safety**: `npm run dev:css` must be running before CSS troubleshooting. Conditional classes/visibility computed server-side (view/context + simple one-line template checks). Planned HTMX targets/swaps documented in Phase 1 contracts.
- [x] **HTMX Failure Handling**: Form POST endpoints return partials to stable containers with validation states; trigger elements stay in DOM (no destructive outer swaps on trigger controls).
- [x] **AI Accountability**: Prompt/response trail remains in feature spec (`Clarifications`) and chat history; PR will reference spec/plan/tasks and this conversation IDs per Principle V.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

### Post-Design Constitution Re-Check

- [x] Research/design artifacts keep scope within `spec.md` clarifications and FR/SC list.
- [x] Data model and contracts preserve deterministic, reversible migration approach and fixture idempotency.
- [x] No dependency additions introduced in design artifacts.
- [x] HTMX contracts explicitly define target/swap and stable container behavior.
- [x] AI-generated decisions are documented in `research.md` and referenced by this plan.

## Project Structure

### Documentation (this feature)

```text
specs/001-household-admin-settings/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
Django apps and templates:
core/
households/
  models.py
  views.py
  services/
pages/
  household_urls.py
templates/
  components/layout/
  registration/
financial/tests/

Feature docs:
specs/001-household-admin-settings/
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/
```

**Structure Decision**: Use the existing Django monolith structure and extend `households` domain + shared layout templates for navigation gating. Keep auth and module access control server-side with targeted HTMX partials for admin settings forms.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
