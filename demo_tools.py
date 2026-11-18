from database import Database
from validation import get_number

def set_vote_count(db,candidate_id,new_count):
    # TAMPER DEMO: changes vote_count but NOT audit_count,so the audit shows NO MATCH
    conn=db.connect()
    cursor=conn.cursor()
    cursor.execute(
        "UPDATE candidates SET vote_count = %s WHERE candidate_id=%s", (new_count, candidate_id),
    )
    conn.commit()
    conn.close()

def reset_votes(db):
    # puts every count back to 0 and lets every voter vote again
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE voters SET has_voted = 0")
    cursor.execute("UPDATE candidates SET vote_count = 0, audit_count = 0")
    conn.commit()
    conn.close()

if __name__ =="__main__":
    db=Database()
    print("DEMO TOOLS- this changes the real data")
    print("1. Tamper with a vote count")
    print("2. Reset all votes")
    choice= input("Choose 1 or 2 (anything else cancels):").strip()

    if choice == "1":
        candidate_id=get_number("Candidate number:",1,3)
        new_count=get_number("New vote_count:",0,100000)
        set_vote_count(db,candidate_id,new_count)
        print("Done. Now run the audit.")
    elif choice=="2":
        if input("Type RESET to confirm:").strip()=="RESET":
            reset_votes(db)
            print("All votes were reset.")
        else:
            print("Cancelled.")
    else:
        print("Cancelled.")    
