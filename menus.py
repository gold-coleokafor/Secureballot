from admin import AdminService
from audit import Audit
from how_to_vote import show_how_to_vote
from validation import get_number
from voting import VotingService
class Menu:
    def __init__(self, db):
        self.db = db

    def show_main_menu(self):
        print("WELCOME TO SECUREBALLOT")
        print("What would you like to do today?")
        print("1. Register voter")
        print("2. Vote")
        print("3. View results")
        print("4. Audit")
        print("5. How to vote")
        print("0. Exit")

    def run(self):
        while True:
            self.show_main_menu()
            choice = get_number("Type a number (0-5) and press Enter: ", 0, 5)

            result = None
            if choice == 1:
                result = AdminService(self.db).run_admin_menu()
            elif choice == 2:
                result = VotingService(self.db).run_vote()
            elif choice == 3:
                result = Audit(self.db).show_results()
            elif choice == 4:
                result = Audit(self.db).show_audit()
            elif choice == 5:
                result = show_how_to_vote()
            elif choice == 0:
                result = "exit"

            if result == "exit":
                print("Goodbye.")
                break
    
