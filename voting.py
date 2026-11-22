"""
voting.py - Voting Service for Secure Ballot System
"""

from database import ELECTION_NAME
from validation import valid_pin


def _candidate_details(item):
    if isinstance(item, dict):
        return item["candidate_id"], item["name"]
    if isinstance(item, (tuple, list)):
        return item[0], item[1]
    candidate_id = getattr(item, "candidate_id", None)
    if candidate_id is None:
        candidate_id = item.id
    return candidate_id, item.name


class VotingService:
    def __init__(self, db):
        """Rule 1: One shared db passed into VotingService [2]."""
        self.db = db

    def run_vote(self):
        """
        Executes the candidate screen, ID/PIN authentication, confirmation,
        and count updates.

        Returns:
            "exit": if user enters 0 to quit system [2].
            None: if user enters 99 or finishes voting [2].
        """
        print("\n" + "=" * 50)
        print(f"       {ELECTION_NAME} - VOTING SCREEN")
        print("=" * 50)
        print("Enter 0 at any prompt to Exit System | 99 for Main Menu\n")

        # Step 1: ID and PIN Check
        voter_id_str = input("Please enter your Voter ID: ").strip()
        if voter_id_str == "0":
            return "exit"
        if voter_id_str == "99":
            return None

        pin_str = input("Please enter your 4-digit PIN: ").strip()
        if pin_str == "0":
            return "exit"
        if pin_str == "99":
            return None

        if not valid_pin(pin_str):
            print("\nError: PIN must be a valid 4-digit number.")
            input("\nPress Enter to return to Main Menu...")
            return None

        if not voter_id_str.isalnum():
            print("\nError: Voter ID must be alphanumeric.")
            input("\nPress Enter to return to Main Menu...")
            return None
        voter_id = voter_id_str
        pin = pin_str

        # Rule 6: Check voter status [2]
        voter = self.db.get_voter(voter_id)
        if not voter:
            print("\nAuthentication Failed: Voter ID not found.")
            input("\nPress Enter to return to Main Menu...")
            return None

        # One vote per voter enforcement
        if getattr(voter, 'has_voted', False):
            print("\nVoting Blocked: You have already cast your vote.")
            input("\nPress Enter to return to Main Menu...")
            return None

        # Rule 5: check_pin() called first [2]
        if not self.db.check_pin(voter_id, pin):
            print("\nAuthentication Failed: Incorrect PIN.")
            input("\nPress Enter to return to Main Menu...")
            return None

        print("\nID & PIN Verified Successfully!")

        # Step 2: Candidate Screen
        # Rule 4: List candidates showing ONLY number and name, NEVER vote_count [2]
        results = self.db.get_results()
        if not results:
            print("\nNo candidates found in database.")
            input("\nPress Enter to return to Main Menu...")
            return None

        print("\n" + "-" * 50)
        print("                 CANDIDATES")
        print("-" * 50)
        candidates = [_candidate_details(item) for item in results]
        candidate_ids = []
        for c_id, c_name in candidates:
            candidate_ids.append(c_id)
            print(f"  [{c_id}] {c_name}")
        print("-" * 50)

        # Candidate Selection
        choice_str = input("\nEnter Candidate Number to vote for (0 to Exit, 99 for Main Menu): ").strip()
        if choice_str == "0":
            return "exit"
        if choice_str == "99":
            return None

        try:
            selected_cid = int(choice_str)
        except ValueError:
            print("\nInvalid candidate selection.")
            input("\nPress Enter to return to Main Menu...")
            return None

        if selected_cid not in candidate_ids:
            print("\nInvalid candidate selection.")
            input("\nPress Enter to return to Main Menu...")
            return None

        selected_name = next(
            name for candidate_id, name in candidates
            if candidate_id == selected_cid
        )

        # Step 3: Confirmation Screen
        print("\n" + "-" * 50)
        print("             CONFIRM YOUR SELECTION")
        print("-" * 50)
        print(f"You are about to vote for: [{selected_cid}] {selected_name}")
        confirm = input("Confirm vote? (1 = Yes, 2 = No / Cancel): ").strip()

        if confirm != "1":
            print("\nVote cancelled. Returning to main menu.")
            input("\nPress Enter to return...")
            return None

        # Step 4: Update Counts
        result = self.db.add_vote(voter_id, selected_cid)
        if result == "ok" or result is True:
            print("\nSuccess: Your vote has been recorded!")
        elif result == "already_voted":
            print("\nVoting Blocked: You have already cast your vote.")
        else:
            print("\nError: Failed to record vote.")

        input("\nPress Enter to return to Main Menu...")
        return None 