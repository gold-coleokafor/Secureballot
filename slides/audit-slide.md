# Slide: Audit — proving the count is honest

**Owner:** Person 5 (Results and audit)
**Time:** 45–60 seconds, straight after the Results slide

---

## Slide text

### Audit: proving the count is honest

- Every vote adds **1 to two separate counters**: `vote_count` and `audit_count`
- **Results** (option 3) shows `vote_count`
- **Audit** (option 4) shows `vote_count / audit_count` → `MATCH` or `NO MATCH`
- It also checks: **total votes = voters who voted** → `All voters counted: YES / NO`
- When a number is wrong, the screen names the record to check

> One line to read: *"A hand-edited results file can change one number — it cannot change both."*

---

## Visual

Clean election:

```
SAMPLE PRESIDENTIAL ELECTION

Candidate A: 12 / 12 MATCH
Candidate B:  9 /  9 MATCH
Candidate C:  4 /  4 MATCH

All voters counted: YES
```

After someone edits Candidate B's `vote_count` with `set_vote_count()`:

```
SAMPLE PRESIDENTIAL ELECTION

Candidate A: 12 / 12 MATCH
Candidate B: 11 /  9 NO MATCH
Candidate C:  4 /  4 MATCH

All voters counted: NO
Check Candidate B records
```

---

## Speaker notes

> "The Results screen shows how many votes each candidate got. But a results
> screen alone can lie — if someone edits the MySQL database, it happily shows
> the wrong number. So each vote also updates a separate audit counter. The
> audit screen puts the two side by side and prints MATCH or NO MATCH.
>
> It also compares the total votes with the number of voters marked as having
> voted. Here Candidate B's results counter was raised by two, so the audit
> reports 27 votes for 25 voters, prints 'All voters counted: NO', and tells the
> officer to check Candidate B's records.
>
> The audit only reads data — it never changes a vote — so it is safe to show
> publicly. That is the screen we use in the tamper demo."

---

## Demo cue

Run `python tamper_demo.py` from the repo root (needs MySQL running and the
`.env` values set). It uses Person 2's `demo_tools.py`:

1. clean audit → all `MATCH`, `YES`
2. `set_vote_count(db, 2, 11)` → `NO MATCH`, `NO`, `Check Candidate B records`
3. `reset_votes(db)` → clean election again

Have the tampered output on screen with this slide visible.

---

## If asked…

**"Why not store who voted for whom?"**
> "That would break the secret ballot. We store one vote per voter and two
> totals — nothing links a voter ID to a candidate."

**"What if someone changes both counters?"**
> "They would also have to change the voters table, which the 'All voters
> counted' check catches. This is still a prototype, not real election security."

**"Is this the real INEC system?"**
> "No. The USSD code is simulated, the data is fake, and it runs on one machine.
> Our limitations slide covers that."
