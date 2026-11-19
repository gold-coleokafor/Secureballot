# SecureBallot — Person 5 (Results and audit)

Files pushed to the group repo:

```
audit.py                 class Audit(db): show_results(), show_audit()
tamper_demo.py           tamper demo using Person 2's demo_tools
test_audit.py            21 unit tests
slides/audit-slide.md    own slide + speaker notes
```

## How Person 1 wires it in

```python
from audit import Audit

self.audit = Audit(db)          # the one shared Database from main()

if choice == 3:
    action = self.audit.show_results()
elif choice == 4:
    action = self.audit.show_audit()

if action == "exit":
    break
```

Return convention followed exactly: `"exit"` when the user types `0`,
`None` when they type `99` (or finish).

## Shapes handled from `database.py`

- `get_results()` → list of dicts with `candidate_id`, `name`, `vote_count`
- `get_audit_counts()` → `{"candidates": [{"name", "vote_count",
  "audit_count"}], "voters_who_voted": <int>}` (the MySQL version), or a plain
  list of rows
- `get_all_voters()` → list of dicts with `has_voted` (bool or Yes/No)

`voters_who_voted` is read from `get_audit_counts()` when present, so the audit
uses the database's own count rather than recounting voters.

## Run

```bash
python -m unittest test_audit -v   # no MySQL needed (fake DB)
python tamper_demo.py              # needs MySQL + .env
```

## Tests

21 tests: results totals, exact screen lines, clean audit, tampered results
counter, tampered audit counter, multiple mismatches, zero-vote election,
voter-count mismatch, missing audit row, read-only behaviour, return values,
and the alternative return shapes.
