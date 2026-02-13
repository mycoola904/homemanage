# homemanage

A structured household finance and account management application built with Django, PostgreSQL, HTMX, TailwindCSS, and DaisyUI.

This project is intended to be a long-term, extensible financial management system for personal use. It emphasizes clarity, correctness, and disciplined development practices over rapid feature sprawl.

---

## Purpose

`homemanage` is designed to:

- Track financial accounts (Checking, Savings, Credit Cards, Loans, etc.)
- Record and manage transactions
- Provide clean UI interactions using HTMX
- Support structured financial analysis and future forecasting
- Serve as a disciplined, spec-driven development environment

This repository is **not** a starter template. It is a concrete application built from a starter foundation.

---

## Tech Stack

- **Python 3.x**
- **Django 5.x**
- **PostgreSQL**
- **HTMX** (dynamic partial rendering)
- **TailwindCSS**
- **DaisyUI**
- **Git + GitHub Issues** for structured feature tracking

No new dependencies were added for the Household Container MVP; implementation uses the existing project stack only.

---

## Architecture Overview

### Backend

- Django project structure
- PostgreSQL database
- Model-driven forms
- Explicit uniqueness constraints at the database level
- Clean separation between feature apps

### Frontend

- TailwindCSS for utility-based styling
- DaisyUI for component styling
- HTMX for partial swaps and dynamic UX
- Reusable global components stored under:

```
templates/components/
```

All shared components are globally defined to maintain UI consistency.

---

## Current Features

### Accounts

- Account list view
- Create account
- Edit account
- Delete account
- HTMX-powered detail panel swapping
- Database-enforced uniqueness for account names
- Manual test-verified CRUD behavior

### Household Container (MVP)

- Household home route at `/household/`
- Finance module mounted at `/household/finance/`
- Session-scoped active household switching in navbar
- Household-scoped account and transaction access guards

### Household Container Non-Goals (FR-016)

- No budget planner, forecasting, analytics dashboard, or reporting features in this MVP
- No role-permission matrix expansion beyond owner/admin/member structure
- No cross-household aggregate financial views in this MVP

---

## Development Workflow

This project follows a disciplined feature-branch workflow:

1. Each feature is developed in its own branch.
2. Features are manually tested before merge.
3. Small defects are fixed immediately.
4. Larger issues are logged via GitHub Issues.
5. `main` must remain stable.
6. Feature branches are deleted after successful merge.

### Definition of Done (General)

A feature is ready to merge when:

- All CRUD paths function correctly
- No unhandled errors occur
- HTMX interactions behave predictably
- Database constraints hold
- No known blocking issues remain

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd homemanage
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the project root.

Include database configuration and Django secret key.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Run development server

```bash
python manage.py runserver
```

### 7. Run Tailwind watcher (if applicable)

```bash
npm run dev:css
```

### 8. Household routes

- Household home: `/household/`
- Finance root: `/household/finance/`
- Household switch action: `/household/switch/`
- No-access page: `/household/no-access/`

---

## Roadmap

Planned future enhancements:

- Category model refactor (move from free-form to relational model)
- Budget modeling system
- Financial risk index tracking
- Reporting dashboards
- CSV transaction import
- Forecasting / projection modules
- Advanced filtering and analytics

---

## Philosophy

This project prioritizes:

- Stability over novelty
- Clarity over cleverness
- Explicit database integrity
- Spec-driven iteration
- Clean Git discipline

It is intended to grow incrementally with confidence.

---

## License

Personal project. Not intended for public distribution at this time.

---

*homemanage — structured household financial clarity.*

