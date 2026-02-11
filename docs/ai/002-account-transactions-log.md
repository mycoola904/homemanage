# AI Session Log: 001-account-transactions

Date: 2026-02-11

## Scope

Design + planning artifacts for Transactions (Account detail + add via HTMX fragments).

## Prompt/Response References

- Clarification Q&A captured in specs/001-account-transactions/spec.md under "Clarifications".
- This file exists to be linked from the PR description to satisfy Constitution Principle V.

## Decisions recorded

- Amount storage: DecimalField(max_digits=10, decimal_places=2)
- Table columns: Posted On, Description, Amount
- Missing/unowned fragments: HTTP 200 with inline not found message
- posted_on default: server-side today
- direction control: radio buttons

## Phase 1: Setup evidence

### T001 Tailwind watcher

Command:

```
npm run dev:css
```

Output:

```
(no stdout/stderr captured before termination)
```

### T002 Baseline tests

Command:

```
C:/Users/micha/Documents/homemanage/.venv/Scripts/python.exe manage.py test
```

Output:

```
Found 15 test(s).
Creating test database for alias 'default'...
Got an error creating the test database: permission denied to create database

Command exited with code 1
```

Follow-up (constitution-compliant SQLite run):

Command:

```
C:/Users/micha/Documents/homemanage/.venv/Scripts/python.exe manage.py test --settings=core.settings_test
```

Output:

```
Found 15 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............
----------------------------------------------------------------------
Ran 15 tests in 11.667s

OK
Destroying test database for alias 'default'...
```

## Phase 6: Validation evidence

### T027 Full test run

Command:

```
C:/Users/micha/Documents/homemanage/.venv/Scripts/python.exe manage.py test --settings=core.settings_test
```

Output:

```
Found 24 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
........................
----------------------------------------------------------------------
Ran 24 tests in 19.863s

OK
Destroying test database for alias 'default'...
```

### T028 Migration check

Command:

```
C:/Users/micha/Documents/homemanage/.venv/Scripts/python.exe manage.py makemigrations --check --settings=core.settings_test
```

Output:

```
No changes detected
```

### T029 Success criteria evidence (manual)

Status: Manual verification passed for SC-001 (timed add flow) and SC-002 (422 inline errors without navigation).
