# agents.md
Persistent constraints, workflow, and “earned lessons” for AI agents working in this repo.
Treat **MUST / MUST NOT** as hard requirements.

---

## 0) Prime Directive

- Prefer **framework-correct** solutions over “clever” or stylistic refactors.
- If unsure, choose the option that is **simpler, testable, and reversible**.
- Avoid inventing APIs or behaviors. Verify against the codebase patterns already present.

---

## 1) Before You Change Anything

### MUST do first
- Identify: “What is the failing behavior?” and “What is the expected behavior?”
- Find the exact file(s) and the smallest reproduction path.
- If troubleshooting UI/styling: **confirm the watcher/dev server is running** *before* analyzing CSS.

### MUST NOT do
- Do not propose broad refactors as a first move.
- Do not change formatting across many files during bug fixes.
- Do not “fix” by adding `location.reload()` or other blunt page-refresh workarounds unless explicitly asked.

---

## 2) Django Templates (Critical)

### Template syntax
- **MUST NOT** split `{% ... %}` template tags across multiple lines.
- **MUST NOT** use multi-line `{# ... #}` Django template comments.
  - Use single-line `{# ... #}` or HTML comments `<!-- ... -->` for multi-line notes.

### Logic placement
- Avoid complex conditionals inside templates.
- Prefer computing booleans/values in views and passing them via context.

### Attributes & class composition
- Avoid embedding `{% if %}` blocks inside HTML attributes when possible.
  Prefer:
  - precomputed class strings in context, or
  - small `{% with %}` assignments, kept on ONE LINE.

---

## 3) HTMX Guidelines

- Prefer targeted swaps (`hx-target`) that preserve stable containers.
- Avoid swapping out the container you need later (common failure mode with `outerHTML`).
- Prefer returning partial templates for HTMX requests.
- On validation errors, return the form partial with errors and an appropriate non-200 status when needed.
- Do not hide underlying state bugs with full reloads.

---

## 4) Tailwind / DaisyUI / Frontend Workflow

### First diagnostic question (MANDATORY)
Before troubleshooting any styling/layout issue, ask:
- “Is the Tailwind/Vite/dev watcher running and rebuilding assets?”
- “Do you see rebuild output in the terminal?”
- “Is the browser cache cleared / hard refresh tried?”

### Asset pipeline
- Prefer diagnosing build pipeline issues before adjusting classes.
- Keep class changes minimal until pipeline is confirmed.

---

## 5) Python / Django Code Style

- Keep changes small and scoped to the problem.
- Add or update tests when behavior changes.
- Prefer explicit names over clever abstractions.
- Avoid introducing new dependencies unless requested.

---

## 6) Git / Branching (when applicable)

- One bugfix = one focused commit (or a small, coherent series).
- Write commit messages that describe behavior change, not file edits.
- Avoid mixing formatting-only changes into functional commits.

---

## 7) Output Format Expectations

When giving instructions or plans:
- Provide steps in order.
- Include file paths.
- Include “what to observe” after each step (expected result).

When writing code:
- Include only the necessary code.
- Avoid placeholder pseudo-code unless asked.

---

## 8) Local Known Pitfalls (Add as you learn)

- Django templates: multiline `{% %}` and multiline `{# #}` are a frequent source of silent parsing issues.
- Styling bugs: watcher not running is the first thing to check.
