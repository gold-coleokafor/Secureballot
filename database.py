import hashlib
import os

import mysql.connector

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ----Settings-----------------------------------
DB_NAME=os.environ.get("DB_NAME", "secureballot")
ADMIN_CODE=os.environ.get("ADMIN_CODE", "ADMIN123")
ELECTION_NAME="SAMPLE PRESIDENTIAL ELECTION"
CANDIDATES=["Candidate A", "Candidate B", "Candidate C"]
SAMPLE_VOTERS=[("V001", "1234"), ("V002", "4321"), ("V003", "1111")]

class Database:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    def connect(self,use_db= True):
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT","3306")),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=self.db_name if use_db else None,

        )

    # ---Database Setup-----------------------------------

    def create_tables(self):
        conn=self.connect(use_db=False)
        cursor=conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        except mysql.connector.Error:
            pass

        cursor.execute(f"USE {self.db_name}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                voter_id VARCHAR (12) PRIMARY KEY,
                pin  CHAR(64) NOT NULL,
                has_voted BOOLEAN NOT NULL DEFAULT FALSE
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id INT AUTO_INCREMENT PRIMARY KEY ,
                 name VARCHAR(100) NOT NULL,
                vote_count INT NOT NULL DEFAULT 0,
                audit_count INT NOT NULL DEFAULT 0
            )
            """)
        conn.commit()
        conn.close()


    def seed_data(self):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM candidates")
        how_many= cursor.fetchone()[0]
        if how_many==0:
            for name in CANDIDATES:
                cursor.execute("INSERT INTO candidates (name) VALUES (%s)", (name,))
        cursor.execute("SELECT COUNT(*) FROM voters")
        voters_in_table= cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if voters_in_table==0:
            for voter_id,pin in SAMPLE_VOTERS:
                self.add_voter(voter_id,pin)

    # --Admin Functions-----------------------------------

    def check_admin(self,code):
        return code== ADMIN_CODE

    # --Voter Functions-----------------------------------

    def hash_pin(self,voter_id, pin):
        text=voter_id + ":" + pin
        return hashlib.sha256(text.encode()).hexdigest()

    def add_voter(self,voter_id, pin):
        conn=self.connect()
        cursor=conn.cursor()
        try:
            cursor.execute("INSERT INTO voters (voter_id, pin) VALUES (%s,%s)", 
                    (voter_id, self.hash_pin(voter_id, pin))
                    )
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            conn.close()


    def get_voter(self,voter_id):
        conn=self.connect()
        cursor=conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT * FROM voters WHERE voter_id=%s", 
    (voter_id,)
        )
        row= cursor.fetchone()
        conn.close()

        if row is None:
            return None
        return {"voter_id": row["voter_id"], "has_voted": bool(row["has_voted"])}


    def check_pin(self,voter_id, pin):
        conn=self.connect()
        cursor=conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT pin FROM voters WHERE voter_id=%s", 
    (voter_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return False
        return row["pin"] == self.hash_pin(voter_id, pin)

    def get_all_voters(self):
        conn=self.connect()
        cursor=conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT voter_id, has_voted FROM voters ORDER BY voter_id")
        rows= cursor.fetchall()
        conn.close()

        voters=[]
        for row in rows:
            voters.append({"voter_id": row["voter_id"], "has_voted": bool(row["has_voted"])})
        return voters

    def delete_voter(self,voter_id):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM voters WHERE voter_id=%s AND has_voted=0", 
    (voter_id,)
        )
        removed= cursor.rowcount
        conn.commit()
        conn.close()
        return removed >0

    # --Voting Functions-----------------------------------

    def add_vote(self,voter_id, candidate_id):
        conn=self.connect()
        cursor=conn.cursor(dictionary=True, buffered=True)
        try:
            # FOR UPDATE locks this voter's row, so the same voter cannot sneak in two votes at the same moment.
            cursor.execute(
                "SELECT has_voted FROM voters WHERE voter_id=%s FOR UPDATE",
                (voter_id,),
            )
            voter= cursor.fetchone()
            if voter is None:
                return "no_voter"
            if voter["has_voted"]:
                return "already_voted"

            cursor.execute(
            
                "UPDATE candidates SET vote_count=vote_count + 1,"
                " audit_count=audit_count + 1 WHERE candidate_id=%s",
                (candidate_id,),
            
            )
            if cursor.rowcount == 0:
                return "no_candidate"

            cursor.execute(
                "UPDATE voters SET has_voted=1 WHERE voter_id=%s",
    (voter_id,)
            )
            conn.commit()
            return "ok"
        finally:
            conn.close()

    # --Results and Audit Functions-----------------------------------

    def get_results(self):
        conn=self.connect()
        cursor= conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT candidate_id, name, vote_count From candidates ORDER BY candidate_id"
        )
        results= cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_audit_counts(self):
        conn=self.connect()
        cursor= conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT name, vote_count, audit_count FROM candidates ORDER BY candidate_id"
        )
        candidates= [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) AS n FROM voters WHERE has_voted=1")
        voters_who_voted= cursor.fetchone()["n"]

        conn.close()
        return {"candidates": candidates, "voters_who_voted": voters_who_voted} 

#--------------Old-style Functions-------------

_db=Database()

def create_tables():
    return _db.create_tables()

def seed_data():
    return _db.seed_data()

def check_admin(code):
    return _db.check_admin(code)

def add_voter(voter_id, pin):
    return _db.add_voter(voter_id, pin)


def get_voter(voter_id):
    return _db.get_voter(voter_id)


def check_pin(voter_id, pin):
    return _db.check_pin(voter_id, pin)


def get_all_voters():
    return _db.get_all_voters()


def delete_voter(voter_id):
    return _db.delete_voter(voter_id)


def add_vote(voter_id, candidate_id):
    return _db.add_vote(voter_id, candidate_id)


def get_results():
    return _db.get_results()


def get_audit_counts():
    return _db.get_audit_counts()


if __name__=="__main__":
    db=Database()
    db.create_tables()
    db.seed_data()
    for candidate in db.get_results():
        print(candidate)



    
    


