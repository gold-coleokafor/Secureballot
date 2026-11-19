import unittest

from models import Voter, Candidate, Admin


class TestVoter(unittest.TestCase):
    def test_new_voter_has_not_voted(self):
        self.assertFalse(Voter("V001").has_voted)

    def test_from_dict_builds_voter(self):
        v = Voter.from_dict({"voter_id": "V002", "has_voted": True})
        self.assertEqual(v.voter_id, "V002")
        self.assertTrue(v.has_voted)

    def test_str_shows_status(self):
        self.assertEqual(str(Voter("V003")), "V003 (not voted yet)")
        self.assertEqual(str(Voter("V003", True)), "V003 (voted)")


class TestCandidate(unittest.TestCase):
    def test_counts_match_when_equal(self):
        self.assertTrue(Candidate(1, "Candidate A", 5, 5).counts_match())

    def test_counts_match_false_when_different(self):
        self.assertFalse(Candidate(2, "Candidate B", 9, 11).counts_match())

    def test_from_dict_builds_candidate(self):
        c = Candidate.from_dict(
            {"candidate_id": 3, "name": "Candidate C", "vote_count": 4, "audit_count": 4}
        )
        self.assertEqual((c.candidate_id, c.name, c.vote_count), (3, "Candidate C", 4))
        self.assertEqual(str(c), "3. Candidate C")

    def test_from_dict_defaults_counts_to_zero(self):
        c = Candidate.from_dict({"candidate_id": 1, "name": "Candidate A"})
        self.assertEqual((c.vote_count, c.audit_count), (0, 0))


class TestAdmin(unittest.TestCase):
    def test_admin_str(self):
        self.assertEqual(str(Admin(1)), "Admin 1")


if __name__ == "__main__":
    unittest.main()
