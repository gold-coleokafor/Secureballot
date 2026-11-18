# validation.py - checks what the user types so the program does not crash

def valid_pin(pin):
    # pin must be exactly 4 digits
    if len(pin)==4 and pin.isdigit():
        return True
    return False


def valid_voter_id(voter_id):
    # a voter ID is 3 to 12 letters or numbers, with no spaces
    if voter_id.isalnum() and 3<= len(voter_id) <=12:
        return True
    return False

   

def get_number(prompt, low, high):
    # keep asking until the user types a whole number
    # the number must be within the given range
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print("Please type a number, not letters.")
            continue
        if low <= number <= high:
            return number
        print("That option is not on the menu.")


def get_voter_id(prompt="Enter Voter ID: "):
    while True:
        voter_id= input(prompt).strip()
        if valid_voter_id(voter_id):
            return voter_id
        print("Voter ID must be 3 to 12 letters or digits, no spaces.")


def get_pin(prompt="Enter PIN: "):
    while True:
        pin=input(prompt).strip()
        if valid_pin(pin):
            return pin
        print("PIN must be exactly 4 digits.")


def get_new_pin():
    # ask for the PIN twice, and repeat until both match
    while True:
        pin= get_pin("Choose a 4-digit PIN: ")
        second_attempt=input("Re-enter your PIN: ").strip()
        if pin==second_attempt:
            return pin
        print("PINs do not match. Try again.")
