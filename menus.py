from validation import get_number

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

    def coming_soon(self, feature_name):
        print(feature_name + " is coming soon.")

    def run(self):
        while True:
            self.show_main_menu()
            choice = get_number("Type a number (0-5) and press Enter: ", 0, 5)

            result = None
            if choice == 1:
                result = self.coming_soon("Register voter")
            elif choice == 2:
                result = self.coming_soon("Vote")
            elif choice == 3:
                result = self.coming_soon("Results")
            elif choice == 4:
                result = self.coming_soon("Audit")
            elif choice == 5:
                result = self.coming_soon("How to vote")
            elif choice == 0:
                result = "exit"

            if result == "exit":
                print("Goodbye.")
                break
    
