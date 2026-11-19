from audit import build_report, join_names, print_screen
from database import Database
from demo_tools import reset_votes, set_vote_count

TAMPER_NAME = "Candidate B"
CHANGE = 2
DEMO_VOTES = {1: 12, 2: 9, 3: 4}


def banner(title):
    print()
    print("=" * 52)
    print(title)
    print("=" * 52)


def seed_demo_votes(db):
    if sum(row["vote_count"] for row in build_report(db)["records"]) > 0:
        return
    number = 1
    for candidate_id, count in DEMO_VOTES.items():
        for _ in range(count):
            voter_id = f"DEMO{number:03d}"
            db.add_voter(voter_id, "1234")
            result = db.add_vote(voter_id, candidate_id)
            if result not in ("ok", True):
                raise SystemExit("Could not record the demo vote.")
            number += 1


def show_audit(db, title):
    banner(title)
    report = build_report(db)
    print_screen(report["audit_lines"])
    return report


def main():
    db = Database()
    db.create_tables()
    db.seed_data()
    seed_demo_votes(db)

    print("SecureBallot tamper demo")

    report = show_audit(db, "STEP 1 - a normal election")
    if not (report["all_match"] and report["all_counted"]):
        raise SystemExit(
            "Demo setup is wrong: the clean election should match."
        )

    records = report["records"]
    candidate = next(
        (row for row in records if row["name"] == TAMPER_NAME), None
    )
    if candidate is None:
        raise SystemExit(f"{TAMPER_NAME} is not in the database.")

    old_count = candidate["vote_count"]
    new_count = old_count + CHANGE
    set_vote_count(db, candidate["candidate_id"], new_count)
    print(f"\nSomeone changed {TAMPER_NAME}'s vote_count: "
          f"{old_count} -> {new_count} (audit_count is still "
          f"{candidate['audit_count']})")

    report = show_audit(db, "STEP 2 - results counter edited by hand")
    if report["all_match"] or report["all_counted"]:
        raise SystemExit("Demo failed: the audit did not catch the change.")
    print(f"\nCaught: {report['total_votes']} votes recorded but "
          f"{report['voted']} voters voted.")
    print(f"Screen says: check {join_names(report['mismatched'])} records.")

    reset_votes(db)
    report = show_audit(db, "STEP 3 - reset_votes() clears the election")
    if not (report["all_match"] and report["all_counted"]):
        raise SystemExit(
            "Demo failed: the election should be clean after reset."
        )

    print("\nDemo complete: the audit caught the change, and the reset "
          "leaves a clean election.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
