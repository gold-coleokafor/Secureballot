from database import Database
from menus import Menu

def main():
    db = Database()
    db.create_tables()
    db.seed_data()

    menu = Menu(db)
    try:
        menu.run()
    except KeyboardInterrupt:
        print("Session interrupted, goodbye!")

if __name__ == "__main__":
    main()
