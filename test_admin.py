import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from admin import AdminService

ADMIN_CODE = "1234"


class FakeDatabase:
    """In-memory stand-in that follows the agreed Database interface."""

    def __init__(self):
        self.voters = {}

    def check_admin(self, code):
        return code == ADMIN_CODE

    def get_voter(self, voter_id):
        return self.voters.get(voter_id)

    def add_voter(self, voter_id, pin):
        if voter_id in self.voters:
            return False
        self.voters[voter_id] = {"pin": pin, "has_voted": False}
        return True

    def delete_voter(self, voter_id):
        voter = self.voters.get(voter_id)
        if voter is None or voter["has_voted"]:
            return False
        del self.voters[voter_id]
        return True


class AdminTests(unittest.TestCase):
    """Tests for AdminService.run_admin_menu()."""

    def setUp(self):
        self.db = FakeDatabase()
        self.admin = AdminService(self.db)

    def run_menu(self, typed, choices):
        """Run the admin menu with scripted typing and menu choices.

        Returns (what run_admin_menu returned, what it printed).
        """
        out = io.StringIO()
        with patch("builtins.input", side_effect=typed), \
                patch("admin.get_number", side_effect=choices), \
                redirect_stdout(out):
            result = self.admin.run_admin_menu()
        return result, out.getvalue()

    # ---- admin code ----
    def test_correct_code_then_main_menu_returns_none(self):
        result, text = self.run_menu([ADMIN_CODE], [99])
        self.assertIsNone(result)
        self.assertIn("1. Register voter", text)
        self.assertIn("2. Remove voter", text)

    def test_choose_zero_returns_exit(self):
        result, _ = self.run_menu([ADMIN_CODE], [0])
        self.assertEqual(result, "exit")

    def test_wrong_code_three_times_returns_none_without_menu(self):
        result, text = self.run_menu(["a", "b", "c"], [])
        self.assertIsNone(result)
        self.assertNotIn("1. Register voter", text)
        self.assertIn("Wrong admin code", text)

    def test_wrong_code_then_correct_code_works(self):
        result, text = self.run_menu(["bad", ADMIN_CODE], [0])
        self.assertEqual(result, "exit")
        self.assertIn("2 attempt(s) left", text)

    def test_blank_admin_code_is_rejected(self):
        result, _ = self.run_menu(["", "  ", ""], [])
        self.assertIsNone(result)

    def test_title_shows_election_name(self):
        import database
        _, text = self.run_menu([ADMIN_CODE], [99])
        self.assertIn(database.ELECTION_NAME, text)

    # ---- register voter ----
    def test_register_voter_success(self):
        _, text = self.run_menu([ADMIN_CODE, "V001", "4321", "4321"], [1, 99])
        self.assertEqual(self.db.voters["V001"]["pin"], "4321")
        self.assertFalse(self.db.voters["V001"]["has_voted"])
        self.assertIn("registered successfully", text)

    def test_voter_id_spaces_are_removed(self):
        self.run_menu([ADMIN_CODE, "  V002  ", "1111", "1111"], [1, 99])
        self.assertIn("V002", self.db.voters)

    def test_empty_voter_id_rejected(self):
        _, text = self.run_menu([ADMIN_CODE, "   "], [1, 99])
        self.assertEqual(self.db.voters, {})
        self.assertIn("cannot be empty", text)

    def test_duplicate_voter_id_rejected(self):
        self.db.add_voter("V001", "1234")
        _, text = self.run_menu([ADMIN_CODE, "V001"], [1, 99])
        self.assertEqual(self.db.voters["V001"]["pin"], "1234")
        self.assertIn("already registered", text)

    def test_pin_with_letters_rejected(self):
        _, text = self.run_menu([ADMIN_CODE, "V003", "abcd"], [1, 99])
        self.assertNotIn("V003", self.db.voters)
        self.assertIn("Invalid PIN", text)

    def test_pin_wrong_length_rejected(self):
        for bad_pin in ("12", "12345", ""):
            self.run_menu([ADMIN_CODE, "V004", bad_pin], [1, 99])
            self.assertNotIn("V004", self.db.voters)

    def test_pin_mismatch_rejected(self):
        _, text = self.run_menu([ADMIN_CODE, "V005", "1234", "4321"], [1, 99])
        self.assertNotIn("V005", self.db.voters)
        self.assertIn("do not match", text)

    def test_add_voter_failure_is_reported(self):
        with patch.object(self.db, "add_voter", return_value=False):
            _, text = self.run_menu([ADMIN_CODE, "V006", "1234", "1234"],
                                    [1, 99])
        self.assertIn("Could not register", text)
        self.assertNotIn("registered successfully", text)

    # ---- remove voter ----
    def test_remove_existing_voter(self):
        self.db.add_voter("V010", "1234")
        _, text = self.run_menu([ADMIN_CODE, "V010"], [2, 99])
        self.assertNotIn("V010", self.db.voters)
        self.assertIn("removed successfully", text)

    def test_remove_unknown_voter(self):
        self.db.add_voter("V011", "1234")
        _, text = self.run_menu([ADMIN_CODE, "NOPE"], [2, 99])
        self.assertIn("not found", text)
        self.assertIn("V011", self.db.voters)

    def test_cannot_remove_voter_who_already_voted(self):
        self.db.add_voter("V012", "1234")
        self.db.voters["V012"]["has_voted"] = True
        _, text = self.run_menu([ADMIN_CODE, "V012"], [2, 99])
        self.assertIn("V012", self.db.voters)
        self.assertIn("already voted", text)

    # ---- menu behaviour ----
    def test_invalid_menu_choice_shows_message_and_continues(self):
        result, text = self.run_menu([ADMIN_CODE], [7, None, 99])
        self.assertIsNone(result)
        self.assertEqual(text.count("Invalid choice"), 2)

    def test_register_then_remove_in_one_session(self):
        typed = [ADMIN_CODE, "V020", "2468", "2468", "V020"]
        result, _ = self.run_menu(typed, [1, 2, 0])
        self.assertEqual(result, "exit")
        self.assertNotIn("V020", self.db.voters)


if __name__ == "__main__":
    unittest.main()

      