"""
how_to_vote.py - How to Vote Information Pages
"""

from database import ELECTION_NAME


def show_how_to_vote():
    """
    Displays multi-page instructions on how to vote in Secure Ballot [1].

    Returns:
        "exit": if user chooses 0 [2].
        None: if user chooses 99 or finishes guide [2].
    """
    pages = [
        {
            "title": "Welcome & Prerequisites",
            "content": (
                "To cast a ballot, you will need:\n"
                "  1. Your unique Numeric Voter ID\n"
                "  2. Your secret 4-digit Security PIN\n\n"
                "Navigation:\n"
                "  • Enter '0' at any prompt to Exit System.\n"
                "  • Enter '99' at any prompt for Main Menu."
            )
        },
        {
            "title": "Authentication & One-Vote Rule",
            "content": (
                "• Enter your Voter ID and PIN when prompted.\n"
                "• ONE VOTE RULE: Each voter ID can only cast one vote.\n"
                "  Subsequent attempts with the same ID are blocked."
            )
        },
        {
            "title": "Selecting a Candidate",
            "content": (
                "• The ballot displays Candidate Numbers and Names.\n"
                "• Vote counts are hidden on the voting screen for privacy.\n"
                "• Enter the number of your preferred candidate."
            )
        },
        {
            "title": "Confirmation & Submission",
            "content": (
                "• Verify your choice on the final confirmation screen.\n"
                "• Press '1' to confirm and cast your vote.\n"
                "• Vote totals are updated automatically upon confirmation."
            )
        }
    ]

    current_page = 0
    while current_page < len(pages):
        page = pages[current_page]
        print("\n" + "=" * 60)
        print(f"   {ELECTION_NAME} - HOW TO VOTE (Page {current_page + 1}/{len(pages)})")
        print("=" * 60)
        print(f"=== {page['title']} ===\n\n{page['content']}")
        print("\n" + "-" * 60)
        print("Options: [N]ext Page | [P]revious Page |  Main Menu |  Exit")

        choice = input("Enter choice: ").strip().lower()
        if choice == "0":
            return "exit"
        elif choice == "99":
            return None
        elif choice in ("n", "next"):
            current_page += 1
        elif choice in ("p", "prev", "previous") and current_page > 0:
            current_page -= 1
        else:
            current_page += 1

    input("\nEnd of guide. Press Enter to return to Main Menu...")
    return None

if __name__ == "__main__":
    show_how_to_vote()