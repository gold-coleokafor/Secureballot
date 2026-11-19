import unittest
import uuid
from unittest.mock import patch


import database
import demo_tools
import validation

def drop_database(name):
    conn=database.Database().connect(use_db=False)
    conn.cursor().execute(f"DROP DATABASE IF EXISTS {name}")
    conn.close()

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.test_db_name="secureballot_test_" + uuid.uuid4().hex[:8]
        self.db = database.Database(self.test_db_name)
        self.db.create_tables()
        self.db.seed_data()

    def tearDown(self):
        drop_database(self.test_db_name)

    def test_seed_data_and_running_it_twice(self):
        self.db.create_tables()
        self.db.seed_data()
        results = self.db.get_results()
        self.assertEqual([r["name"]for r in results],
                         ["Candidate A", "Candidate B", "Candidate C"])
        self.assertTrue(all(r["vote_count"]==0 for r in results))
        self.assertEqual(len(self.db.get_all_voters()),3)

    def test_removed_voter_does_not_come_back_after_restart(self):
        self.assertTrue(self.db.delete_voter("V003"))
        self.db.seed_data()
        self.assertIsNone(self.db.get_voter("V003"))
        self.assertEqual(len(self.db.get_all_voters()), 2)

    def test_two_databases_do_not_share_data(self):
        other_name="secureballot_test_"+ uuid.uuid4().hex[:8]
        try:
            other=database.Database(other_name)
            other.create_tables()
            self.assertEqual(other.get_all_voters(), [])
            self.assertEqual(len(self.db.get_all_voters()), 3)
        finally:
            drop_database(other_name)

    def test_duplicate_voter_id_is_refused(self):
        self.assertTrue(self.db.add_voter("V100", "9999"))
        self.assertFalse(self.db.add_voter("V100", "8888"))
        self.assertEqual(self.db.get_voter("V100"), {"voter_id": "V100", "has_voted": False})
        self.assertIsNone(self.db.get_voter("NOBODY"))

    def test_pin_check_and_pin_not_plain_text(self):
        self.assertTrue(self.db.check_pin("V001", "1234"))
        self.assertFalse(self.db.check_pin("V001", "0000"))
        self.assertFalse(self.db.check_pin("NOBODY", "1234"))
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT pin FROM voters WHERE voter_id = 'V001'")
        saved = cursor.fetchone()[0]
        conn.close()
        self.assertNotEqual(saved, "1234")

    def test_check_admin(self):
        self.assertTrue(self.db.check_admin(database.ADMIN_CODE))
        self.assertFalse(self.db.check_admin("wrong"))

    def test_vote_updates_both_counts_and_blocks_second_vote(self):
        self.assertEqual(self.db.add_vote("V001", 2), "ok")
        self.assertEqual(self.db.get_results()[1]["vote_count"], 1)
        audit = self.db.get_audit_counts()
        self.assertEqual(audit["candidates"][1]["audit_count"], 1)
        self.assertEqual(audit["voters_who_voted"], 1)
        self.assertTrue(self.db.get_voter("V001")["has_voted"])
        self.assertEqual(self.db.add_vote("V001", 1), "already_voted")
        self.assertEqual(self.db.get_results()[0]["vote_count"], 0)

    def test_unknown_voter_or_candidate(self):
        self.assertEqual(self.db.add_vote("NOBODY", 1), "no_voter")
        self.assertEqual(self.db.add_vote("V001", 99), "no_candidate")
        self.assertFalse(self.db.get_voter("V001")["has_voted"])

    def test_delete_voter(self):
        self.assertTrue(self.db.delete_voter("V003"))
        self.assertIsNone(self.db.get_voter("V003"))
        self.assertFalse(self.db.delete_voter("V003"))

    def test_voter_who_already_voted_cannot_be_deleted(self):
        self.db.add_vote("V001", 1)
        self.assertFalse(self.db.delete_voter("V001"))
        self.assertEqual(self.db.get_audit_counts()["voters_who_voted"], 1)

    def test_sql_injection_text_is_just_text(self):
        self.assertIsNone(self.db.get_voter("V001' OR '1'='1"))

    def test_old_style_functions_still_work(self):
        # code written as database.add_vote(...) must not break
        real_db = database._db
        database._db = self.db            # point the old-style functions at the test database
        try:
            self.assertTrue(database.check_admin(database.ADMIN_CODE))
            self.assertEqual(database.add_vote("V001", 2), "ok")
            self.assertEqual(database.add_vote("V001", 2), "already_voted")
            self.assertEqual(database.get_results()[1]["vote_count"], 1)
            self.assertEqual(database.get_audit_counts()["voters_who_voted"], 1)
            self.assertTrue(database.add_voter("V200", "5555"))
            self.assertTrue(database.check_pin("V200", "5555"))
            self.assertTrue(database.delete_voter("V200"))
            self.assertEqual(len(database.get_all_voters()), 3)
        finally:
            database._db = real_db

    def test_demo_tools_tamper_then_reset(self):
        self.db.add_vote("V001", 1)
        self.db.add_vote("V002", 2)
        audit = self.db.get_audit_counts()
        self.assertTrue(all(c["vote_count"] == c["audit_count"] for c in audit["candidates"]))
        self.assertEqual(sum(c["vote_count"] for c in audit["candidates"]),
                         audit["voters_who_voted"])

        demo_tools.set_vote_count(self.db, 2, 11)
        tampered = self.db.get_audit_counts()["candidates"][1]
        self.assertNotEqual(tampered["vote_count"], tampered["audit_count"])

        demo_tools.reset_votes(self.db)
        self.assertEqual(self.db.get_audit_counts()["voters_who_voted"], 0)
        self.assertFalse(self.db.get_voter("V001")["has_voted"])


class ValidationTests(unittest.TestCase):
    def test_valid_pin_and_voter_id(self):
        self.assertTrue(validation.valid_pin("1234"))
        self.assertFalse(any(validation.valid_pin(p) for p in ["", "123", "12345", "12a4"]))
        self.assertTrue(validation.valid_voter_id("V001"))
        self.assertFalse(any(validation.valid_voter_id(v) for v in ["", "V", "V 01", "A" * 13]))

    def test_get_number_retries_until_valid(self):
        with patch("builtins.input", side_effect=["abc", "9", "2"]), patch("builtins.print"):
            self.assertEqual(validation.get_number("> ", 1,  3), 2)
        with patch("builtins.input", side_effect=["x", "42"]), patch("builtins.print"):
            self.assertEqual(validation.get_number("> ",0,100), 42)

    def test_get_new_pin_retries_when_different(self):
        with patch("builtins.input", side_effect=["1234", "9999", "4321", "4321"]), patch("builtins.print"):
            self.assertEqual(validation.get_new_pin(), "4321")


if __name__ == "__main__":
    unittest.main()






    

