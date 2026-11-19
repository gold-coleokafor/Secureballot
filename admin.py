"""Admin screens for SecureBallot (Person 3).

Checks the admin code, registers voters and removes voters.
"""
from database import ELECTION_NAME
from validation import get_number, valid_pin

MAX_CODE_ATTEMPTS = 3


class AdminService:
    """Handles the registration officer's role: register and remove voters."""

    def __init__(self, db):
        """Keep the single shared Database that main.py created.

        Args:
            db: The shared Database object.
        """
        self.db = db

    def run_admin_menu(self):
        """Check the admin code, then show the admin menu until done.

        Returns:
            "exit" if the user chose 0, otherwise None (user chose 99, or the
            admin code was wrong too many times).
        """
        self._header("ADMIN")
        if not self._check_admin_code():
            return None

        while True:
            self._show_menu()
            choice = get_number("Type a number and press Enter: ", 0, 99)
            if choice == 0:
                return "exit"
            if choice == 99:
                return None
            if choice == 1:
                self._register_voter()
            elif choice == 2:
                self._remove_voter()
            else:
                print("Invalid choice. Please try again.")

    def _header(self, title):
        """Print a screen title with the election name."""
        print("=" * 50)
        print(title)
        print(ELECTION_NAME)
        print("=" * 50)

    def _show_menu(self):
        """Print the admin menu."""
        print()
        self._header("ADMIN MENU")
        print("1. Register voter")
        print("2. Remove voter")
        print("99. Main menu   0. Exit")

    def _check_admin_code(self):
        """Ask for the admin code, allowing a few attempts.

        Returns:
            True if the code was correct, otherwise False.
        """
        for attempt in range(MAX_CODE_ATTEMPTS):
            code = input("Enter admin code: ").strip()
            if self.db.check_admin(code):
                return True
            left = MAX_CODE_ATTEMPTS - attempt - 1
            if left:
                print("Wrong admin code. {} attempt(s) left.".format(left))
        print("Wrong admin code. Returning to the main menu.")
        return False

    def _register_voter(self):
        """Register a new voter with a voter ID and a 4-digit PIN."""
        voter_id = input("Enter new Voter ID: ").strip()
        if not voter_id:
            print("Voter ID cannot be empty.")
            return
        if self.db.get_voter(voter_id):
            print("This Voter ID is already registered.")
            return

        pin = input("Choose a 4-digit PIN: ").strip()
        if not valid_pin(pin):
            print("Invalid PIN. It must be exactly 4 digits.")
            return
        if input("Re-enter your PIN: ").strip() != pin:
            print("The PINs do not match. Voter not registered.")
            return

        if self.db.add_voter(voter_id, pin) is False:
            print("Could not register the voter. Please try again.")
            return
        print("Voter was registered successfully.")

    def _remove_voter(self):
        """Remove a voter who has not voted yet.

        get_voter() is called first because delete_voter() returns False both
        when the voter does not exist and when the voter has already voted.
        """
        voter_id = input("Enter Voter ID to remove: ").strip()
        if not self.db.get_voter(voter_id):
            print("Voter ID not found.")
        elif self.db.delete_voter(voter_id):
            print("Voter was removed successfully.")
        else:
            print("This voter has already voted and cannot be removed.")