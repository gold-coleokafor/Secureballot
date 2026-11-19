import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from menus import Menu


class MenuTests(unittest.TestCase):
    """Tests for Menu.run() in menus.py."""

    def setUp(self):
        self.db = object()  # stand-in: Menu only passes it to the screens
        self.menu = Menu(self.db)

    def run_menu(self, choices):
        """Run the menu with scripted menu choices; return what it printed."""
        out = io.StringIO()
        with patch("menus.get_number", side_effect=choices), redirect_stdout(out):
            self.menu.run()
        return out.getvalue()

    def test_menu_shows_all_options(self):
        text = self.run_menu([0])
        self.assertIn("WELCOME TO SECUREBALLOT", text)
        for line in ("1. Register voter", "2. Vote", "3. View results",
                     "4. Audit", "5. How to vote", "0. Exit"):
            self.assertIn(line, text)

    def test_choose_zero_says_goodbye(self):
        self.assertIn("Goodbye.", self.run_menu([0]))

    def test_option_1_opens_admin_menu(self):
        with patch("menus.AdminService") as admin_class:
            admin_class.return_value.run_admin_menu.return_value = None
            self.run_menu([1, 0])
        admin_class.assert_called_once_with(self.db)
        admin_class.return_value.run_admin_menu.assert_called_once()

    def test_option_2_opens_voting(self):
        with patch("menus.VotingService") as voting_class:
            voting_class.return_value.run_vote.return_value = None
            self.run_menu([2, 0])
        voting_class.assert_called_once_with(self.db)
        voting_class.return_value.run_vote.assert_called_once()

    def test_option_3_shows_results(self):
        with patch("menus.Audit") as audit_class:
            audit_class.return_value.show_results.return_value = None
            self.run_menu([3, 0])
        audit_class.assert_called_once_with(self.db)
        audit_class.return_value.show_results.assert_called_once()

    def test_option_4_shows_audit(self):
        with patch("menus.Audit") as audit_class:
            audit_class.return_value.show_audit.return_value = None
            self.run_menu([4, 0])
        audit_class.assert_called_once_with(self.db)
        audit_class.return_value.show_audit.assert_called_once()

    def test_option_5_shows_how_to_vote(self):
        with patch("menus.show_how_to_vote", return_value=None) as screen:
            self.run_menu([5, 0])
        screen.assert_called_once()

    def test_screen_returning_exit_stops_the_menu(self):
        with patch("menus.AdminService") as admin_class:
            admin_class.return_value.run_admin_menu.return_value = "exit"
            text = self.run_menu([1])  # no second choice: the loop must stop
        self.assertIn("Goodbye.", text)

    def test_screen_returning_none_shows_menu_again(self):
        with patch("menus.VotingService") as voting_class:
            voting_class.return_value.run_vote.return_value = None
            text = self.run_menu([2, 0])
        self.assertEqual(text.count("WELCOME TO SECUREBALLOT"), 2)

    def test_letters_and_wrong_numbers_do_not_crash(self):
        out = io.StringIO()
        with patch("builtins.input", side_effect=["abc", "9", "0"]) as fake_input, \
                redirect_stdout(out):
            self.menu.run()
        self.assertEqual(fake_input.call_count, 3)
        self.assertIn("Goodbye.", out.getvalue())


if __name__ == "__main__":
    unittest.main()