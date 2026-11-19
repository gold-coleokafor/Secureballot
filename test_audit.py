import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import audit
from database import ELECTION_NAME

NAMES = ["Candidate A", "Candidate B", "Candidate C"]


class FakeDB:
    def __init__(self, votes=(0, 0, 0), voted=0):
        self.candidates = [
            {
                "candidate_id": index + 1,
                "name": name,
                "vote_count": count,
                "audit_count": count,
            }
            for index, (name, count) in enumerate(zip(NAMES, votes))
        ]
        self.voted = voted

    def _find(self, name):
        return next(
            (row for row in self.candidates if row["name"] == name), None
        )

    def set_vote_count(self, name, value):
        row = self._find(name)
        if row is None:
            raise KeyError(name)
        row["vote_count"] = value

    def set_audit_count(self, name, value):
        row = self._find(name)
        if row is None:
            raise KeyError(name)
        row["audit_count"] = value

    def remove_audit_row(self, name):
        self._audit_missing = name

    def get_results(self):
        return [
            {
                "candidate_id": row["candidate_id"],
                "name": row["name"],
                "vote_count": row["vote_count"],
            }
            for row in self.candidates
        ]

    def get_audit_counts(self):
        missing = getattr(self, "_audit_missing", None)
        return {
            "candidates": [
                {
                    "name": row["name"],
                    "vote_count": row["vote_count"],
                    "audit_count": row["audit_count"],
                }
                for row in self.candidates
                if row["name"] != missing
            ],
            "voters_who_voted": self.voted,
        }

    def get_all_voters(self):
        return [
            {"voter_id": f"V{number:03d}", "has_voted": number <= self.voted}
            for number in range(1, self.voted + 1)
        ]


class ResultsScreenTests(unittest.TestCase):
    def test_new_election_shows_zero_for_each_candidate(self):
        report = audit.build_report(FakeDB())

        self.assertEqual(report["total_votes"], 0)
        self.assertEqual(report["results_lines"][0], ELECTION_NAME)
        self.assertIn("Candidate A: 0", "\n".join(report["results_lines"]))

    def test_results_match_the_counts_in_the_database(self):
        report = audit.build_report(FakeDB(votes=(12, 9, 4), voted=25))

        self.assertEqual(report["total_votes"], 25)
        self.assertIn("Candidate A: 12", report["results_lines"])
        self.assertIn("Candidate B:  9", report["results_lines"])
        self.assertIn("Candidate C:  4", report["results_lines"])

    def test_results_screen_has_no_double_counter_column(self):
        report = audit.build_report(FakeDB(votes=(2, 0, 0), voted=2))
        for line in report["results_lines"]:
            self.assertNotIn("/", line)


class AuditScreenTests(unittest.TestCase):
    def test_clean_election_is_all_match_and_all_counted(self):
        report = audit.build_report(FakeDB(votes=(12, 9, 4), voted=25))

        self.assertTrue(report["all_match"])
        self.assertTrue(report["all_counted"])
        self.assertEqual(report["mismatched"], [])
        self.assertEqual(report["voted"], 25)
        self.assertIn("Candidate A: 12 / 12 MATCH", report["audit_lines"])
        self.assertIn("Candidate B:  9 /  9 MATCH", report["audit_lines"])
        self.assertIn("All voters counted: YES", report["audit_lines"])

    def test_changed_results_counter_is_caught(self):
        db = FakeDB(votes=(12, 9, 4), voted=25)
        db.set_vote_count("Candidate B", 11)

        report = audit.build_report(db)

        self.assertFalse(report["all_match"])
        self.assertFalse(report["all_counted"])
        self.assertEqual(report["mismatched"], ["Candidate B"])
        self.assertTrue(any("Candidate B" in line and "NO MATCH" in line
                            for line in report["audit_lines"]))
        self.assertIn("All voters counted: NO", report["audit_lines"])
        self.assertIn("Check Candidate B records", report["audit_lines"])

    def test_changed_audit_counter_is_caught(self):
        db = FakeDB(votes=(2, 0, 0), voted=2)
        db.set_audit_count("Candidate A", 1)

        report = audit.build_report(db)

        self.assertFalse(report["all_match"])
        self.assertEqual(report["mismatched"], ["Candidate A"])
        self.assertTrue(report["all_counted"])

    def test_all_mismatched_candidates_are_named(self):
        db = FakeDB(votes=(2, 2, 2), voted=6)
        db.set_vote_count("Candidate A", 3)
        db.set_vote_count("Candidate C", 3)

        report = audit.build_report(db)

        self.assertEqual(report["mismatched"], ["Candidate A", "Candidate C"])
        self.assertIn("Check Candidate A and Candidate C records",
                      report["audit_lines"])

    def test_zero_vote_election_is_a_match(self):
        report = audit.build_report(FakeDB())

        self.assertTrue(report["all_match"])
        self.assertTrue(report["all_counted"])
        self.assertIn("Candidate A: 0 / 0 MATCH", report["audit_lines"])
        self.assertIn("All voters counted: YES", report["audit_lines"])

    def test_fewer_voters_than_votes_makes_the_total_wrong(self):
        report = audit.build_report(FakeDB(votes=(2, 0, 0), voted=1))

        self.assertFalse(report["all_counted"])
        self.assertIn("All voters counted: NO", report["audit_lines"])

    def test_missing_audit_row_shows_n_a_and_no_match(self):
        db = FakeDB(votes=(1, 0, 0), voted=1)
        db.remove_audit_row("Candidate B")

        lines = audit.build_report(db)["audit_lines"]

        self.assertIn("Candidate B: 0 / n/a NO MATCH", lines)

    def test_voters_who_voted_comes_from_get_audit_counts(self):
        class NoVoters(FakeDB):
            def get_all_voters(self):
                raise AssertionError("should not need get_all_voters")

        report = audit.build_report(NoVoters(votes=(3, 0, 0), voted=3))
        self.assertEqual(report["voted"], 3)
        self.assertTrue(report["all_counted"])

    def test_audit_does_not_change_the_database(self):
        db = FakeDB(votes=(3, 0, 0), voted=3)
        before = [dict(row) for row in db.get_results()]

        audit.build_report(db)

        self.assertEqual(before, db.get_results())


class MergeFriendlyTests(unittest.TestCase):
    class Bare:
        def __init__(self, results, audits, voters=None):
            self.results = results
            self.audits = audits
            self.voters = voters

        def get_results(self):
            return self.results

        def get_audit_counts(self):
            return self.audits

        def get_all_voters(self):
            if self.voters is None:
                raise AttributeError("no get_all_voters")
            return self.voters

    def test_plain_list_of_audit_rows(self):
        db = self.Bare(
            [(1, "Candidate A", 4)], [(1, "Candidate A", 4)],
            [{"has_voted": True}],
        )
        report = audit.build_report(db)

        self.assertEqual(report["records"][0]["audit_count"], 4)
        self.assertTrue(report["all_match"])
        self.assertEqual(report["voted"], 1)

    def test_name_to_count_dictionary(self):
        db = self.Bare({"Candidate A": 3}, {"Candidate A": 3}, [])
        report = audit.build_report(db)

        self.assertEqual(report["records"][0]["vote_count"], 3)
        self.assertTrue(report["all_match"])

    def test_bool_and_yes_flags_are_both_counted(self):
        voters = [{"has_voted": True}, {"has_voted": "yes"},
                  {"has_voted": "No"}]
        db = self.Bare([], [], voters)
        self.assertEqual(audit.count_voters_who_voted(db), 2)

    def test_unknown_voter_count_is_not_guessed(self):
        db = self.Bare([], [], None)
        self.assertIsNone(audit.count_voters_who_voted(db))


class ReturnConventionTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB(votes=(12, 9, 4), voted=25)
        self.screen = audit.Audit(self.db)

    def run_screen(self, screen, keys):
        buffer = io.StringIO()
        with mock.patch("builtins.input", side_effect=keys):
            with redirect_stdout(buffer):
                result = screen()
        return result, buffer.getvalue()

    def test_show_results_returns_none_on_99(self):
        result, output = self.run_screen(self.screen.show_results, ["99"])
        self.assertIsNone(result)
        self.assertIn(audit.FOOTER, output)

    def test_show_results_returns_exit_on_0(self):
        result, _ = self.run_screen(self.screen.show_results, ["0"])
        self.assertEqual(result, "exit")

    def test_show_audit_returns_none_on_99(self):
        result, output = self.run_screen(self.screen.show_audit, ["99"])
        self.assertIsNone(result)
        self.assertIn("All voters counted", output)

    def test_show_audit_returns_exit_on_0(self):
        result, _ = self.run_screen(self.screen.show_audit, ["0"])
        self.assertEqual(result, "exit")

    def test_letters_then_99_do_not_crash(self):
        result, output = self.run_screen(self.screen.show_audit, ["abc", "99"])
        self.assertIsNone(result)
        self.assertIn("Please type a number", output)


if __name__ == "__main__":
    unittest.main()
