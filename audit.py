from database import ELECTION_NAME
from validation import get_number

YES_VALUES = ("yes", "y", "true", "1")
FOOTER = "99. Main menu    0. Exit"


def _field(obj, names):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if not callable(value):
                return value
        try:
            if name in obj.keys():
                return obj[name]
        except (TypeError, AttributeError):
            pass
    return None


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, dict):
        return list(value.values())
    return list(value)


def _rows(raw, count_names, id_names=("candidate_id", "id"),
          name_names=("name", "candidate", "candidate_name")):
    if raw is None:
        return []
    if isinstance(raw, dict) and _field(raw, name_names) is None:
        raw = [{"name": k, "count": v} for k, v in raw.items()]

    rows = []
    for item in _as_list(raw):
        count = _field(item, count_names)
        if count is None and isinstance(item, dict):
            count = item.get("count")
        if count is None and isinstance(item, (tuple, list)):
            parts = list(item)
            if len(parts) >= 3:
                rows.append({"id": parts[0], "name": str(parts[1]),
                             "count": int(parts[2])})
                continue
            if len(parts) == 2:
                rows.append({"id": None, "name": str(parts[0]),
                             "count": int(parts[1])})
                continue
            continue

        name = _field(item, name_names)
        rows.append({
            "id": _field(item, id_names),
            "name": str(name) if name is not None else "",
            "count": int(count) if count is not None else None,
        })
    return rows


def _is_yes(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in YES_VALUES


def load_audit(db):
    raw = db.get_audit_counts()
    if isinstance(raw, dict) and "candidates" in raw:
        rows = _rows(raw["candidates"], ("audit_count", "audit"))
        reported = raw.get("voters_who_voted")
        return rows, int(reported) if reported is not None else None
    return _rows(raw, ("audit_count", "audit")), None


def load_candidates(db, audit_rows=None):
    if audit_rows is None:
        audit_rows, _ = load_audit(db)
    results = _rows(db.get_results(), ("vote_count", "votes", "count"))

    by_id = {
        row["id"]: row["count"] for row in audit_rows if row["id"] is not None
    }
    by_name = {
        row["name"].strip().lower(): row["count"] for row in audit_rows
    }

    records = []
    for position, row in enumerate(results, start=1):
        key = row["name"].strip().lower()
        if row["id"] is not None and row["id"] in by_id:
            audit_count = by_id[row["id"]]
        elif key in by_name:
            audit_count = by_name[key]
        else:
            audit_count = None
        records.append({
            "candidate_id": (
                row["id"] if row["id"] is not None else position
            ),
            "name": row["name"],
            "vote_count": row["count"] if row["count"] is not None else 0,
            "audit_count": audit_count,
        })
    return records


def count_voters_who_voted(db):
    try:
        voters = _as_list(db.get_all_voters())
    except (AttributeError, TypeError):
        return None
    return sum(1 for voter in voters
               if _is_yes(_field(voter, ("has_voted", "voted"))))


def total_votes(records):
    return sum(record["vote_count"] for record in records)


def mismatched_candidates(records):
    return [
        record["name"] for record in records
        if record["audit_count"] is None
        or record["vote_count"] != record["audit_count"]
    ]


def join_names(names):
    names = list(names)
    if len(names) <= 1:
        return "".join(names)
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])} and {names[-1]}"


def format_results(records):
    name_width = max((len(record["name"]) for record in records), default=0)
    count_width = max((len(str(record["vote_count"])) for record in records),
                      default=1)
    lines = [ELECTION_NAME, ""]
    for record in records:
        name = f"{record['name']:<{name_width}}"
        count = f"{record['vote_count']:>{count_width}}"
        lines.append(f"{name}: {count}")
    return lines


def format_audit(records, voted):
    name_width = max((len(record["name"]) for record in records), default=0)
    left_width = max((len(str(record["vote_count"])) for record in records),
                     default=1)
    right_values = [
        "n/a" if record["audit_count"] is None else str(record["audit_count"])
        for record in records
    ]
    right_width = max((len(value) for value in right_values), default=1)

    lines = [ELECTION_NAME, ""]
    for record, right in zip(records, right_values):
        match = (record["audit_count"] is not None
                 and record["vote_count"] == record["audit_count"])
        verdict = "MATCH" if match else "NO MATCH"
        name = f"{record['name']:<{name_width}}"
        left = f"{record['vote_count']:>{left_width}}"
        lines.append(f"{name}: {left} / {right:>{right_width}} {verdict}")

    lines.append("")
    if voted is None:
        lines.append("All voters counted: UNKNOWN")
    else:
        counted = total_votes(records) == voted
        lines.append(f"All voters counted: {'YES' if counted else 'NO'}")

    bad = mismatched_candidates(records)
    if bad:
        lines.append(f"Check {join_names(bad)} records")
    return lines


def build_report(db):
    audit_rows, reported_voted = load_audit(db)
    records = load_candidates(db, audit_rows)
    if reported_voted is not None:
        voted = reported_voted
    else:
        voted = count_voters_who_voted(db)
    bad = mismatched_candidates(records)
    return {
        "records": records,
        "voted": voted,
        "total_votes": total_votes(records),
        "all_match": not bad,
        "all_counted": (
            None if voted is None else total_votes(records) == voted
        ),
        "mismatched": bad,
        "results_lines": format_results(records),
        "audit_lines": format_audit(records, voted),
    }


def print_screen(lines):
    print()
    for line in lines:
        print(line)


def footer():
    print()
    print(FOOTER)
    choice = get_number("> ", 0, 99)
    return "exit" if choice == 0 else None


class Audit:
    def __init__(self, db):
        self.db = db

    def show_results(self):
        print_screen(build_report(self.db)["results_lines"])
        return footer()

    def show_audit(self):
        print_screen(build_report(self.db)["audit_lines"])
        return footer()
