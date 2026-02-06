# Django Golden Starter

A clean, opinionated Django starter project with HTMX, Tailwind CSS, DaisyUI, and AI-agent guardrails baked in.
Designed for rapid development without rediscovering known pitfalls.
***
## Why this repo exists
This starter exists to:
- Avoid repeating known Django + frontend mistakes  
- Encode hard-won lessons (template parsing, HTMX swaps, watcher issues)  
- Provide a stable base for small to medium Django projects  
- Enable productive use of VS Code AI Agents with enforced constraints

This is not a tutorial repo.<br>
It is a working baseline.

## Stack
- Backend: Django
- Frontend: HTMX
- Styling: Tailwind CSS + DaisyUI
- Tooling: Node.js (for Tailwind), Python venv
- Editor: VS Code (recommended)
- AI: VS Code Copilot Agents (repo-aware)

## Project Structure

    ├─ agents.md      # Hard constraints & learned pitfalls for AI agents <br>
    ├─ manage.py<br>
    ├─ core/                     # Django project settings<br>
    ├─ apps/                     # Django apps live here<br>
    ├─ templates/<br>
    ├─ static/<br>
    ├─ .github/<br>
    │  └─ agents/                # VS Code custom agents (repo-scoped)<br>
    ├─ README.md<br>

## AI Agent Usage (Important)

This repository is designed to be used with VS Code’s built-in Agents feature.

### Key files
- agents.md <br>
Defines non-negotiable rules, diagnostic order, and known pitfalls
(e.g., Django template parsing rules, “check the watcher first”).

- .github/agents/*
Custom VS Code agents configured to read and obey agents.md.

### Rule
> Any AI agent working in this repo must read and follow agents.md
MUST / MUST NOT rules are hard constraints.

This prevents the AI from:
- reintroducing known bugs
- “prettifying” code in unsafe ways
- skipping basic diagnostics

## Development Setup
### 1. Python environment

````bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````
### 2. Node & Tailwind
````bash
npm install
npm run dev   # or npm run watch
````
⚠️ **Important:**
If styles are not updating, confirm the watcher is running before debugging CSS.

## Django Templates: Known Constraints
This repo intentionally enforces the following:

- {% ... %} template tags must be single-line
- {# ... #} Django comments must be single-line
- Multi-line comments should use HTML comments
- Complex logic belongs in views, not templates<br>

These rules exist because Django’s template parser is line-sensitive and can fail silently.

## HTMX Guidelines

- Prefer targeted swaps (hx-target)
- Avoid swapping out containers you need later
- Return partial templates for HTMX requests
- Avoid location.reload() as a workaround

## Philosophy

- Prefer correctness over cleverness
- Prefer small, reversible changes
- Prefer explicit logic over magic
- Encode experience in files, not memory
- This repo is meant to feel boring in the best possible way.

## When to use this starter

Use this repo if you want:
- A personal Django baseline
- A consistent starting point for new projects
- An AI-assisted workflow with guardrails
- Fewer “why is this broken?” moments
- Do not use this repo if you want:
- experimental framework churn
- heavy abstraction layers
- tutorial-style scaffolding

## License
Personal / internal use.<br>
Adapt freely for your own projects.