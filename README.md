# SecureBallot

**A transparent voting and audit prototype for the Governance and Infrastructure challenges**

SecureBallot is a menu-driven Python command-line application that simulates a USSD-style phone menu. Registered voters cast their votes directly, the program adds each vote to the candidate's total, and anyone can run a public audit to check that the records still agree. It is a small prototype built with fake data.

> African Leadership University (ALU) | BSE Year 1, Trimester 2 | Peer Learning Project 2 (PLP 2) | Group 17

---

## Contents

1. [The problem](#the-problem)
2. [What SecureBallot does](#what-secureballot-does)
3. [How it works](#how-it-works)
4. [Project structure](#project-structure)
5. [Requirements](#requirements)
6. [Setup and installation](#setup-and-installation)
7. [Running the application](#running-the-application)
8. [Sample data](#sample-data)
9. [Running the tests](#running-the-tests)
10. [Demo: simulating tampering](#demo-simulating-tampering)
11. [Input validation and error handling](#input-validation-and-error-handling)
12. [Limitations](#limitations)
13. [Troubleshooting](#troubleshooting)
14. [Team and contributions](#team-and-contributions)

---

## The problem

Public trust in election results can be weakened by delays, limited transparency, and manual handling of results. In Nigeria's 2023 general elections, the European Union Election Observation Mission reported that only about 20% of presidential result forms had been uploaded to the INEC Results Viewing Portal (IReV) by noon on 26 February 2023. An INEC witness also told the presidential election petition tribunal that results were collated manually. Voters with limited internet access are also easy to leave out of digital election services.

SecureBallot explores a different approach. Nobody types in the final totals, each voter can vote once, votes stay secret, and the public can check whether the records match. The menu is designed to work like a USSD phone code, which runs on basic phones without internet. The full problem statement and references are in our PLP 1 Requirements Specification Document.

## What SecureBallot does

The main menu has six options:

| Option | Feature | What it does |
|---|---|---|
| 1 | Register voter | An admin (registration officer) enters the admin code, then registers a voter with a voter ID and a 4-digit PIN chosen by the voter. The admin menu also lets the officer remove a voter who has not voted yet. |
| 2 | Vote | The voter enters their voter ID and PIN, picks a candidate, then confirms. Each voter can vote only once. |
| 3 | View results | Shows each candidate's total. Open to everyone, no PIN needed. |
| 4 | Audit | Compares each candidate's results count with a separately stored audit count (MATCH or NO MATCH), then checks that the total of all votes equals the number of voters who voted. Open to everyone. |
| 5 | How to vote | Short instruction pages for first-time voters. |
| 0 | Exit | Closes the application. |

On every sub-screen, **99** returns to the main menu and **0** exits.

### CRUD operations

| Operation | Where it happens |
|---|---|
| **Create** | Registering a voter |
| **Read** | Viewing results and the audit |
| **Update** | Casting a vote updates the candidate's counts and marks the voter as having voted |
| **Delete** | The admin removes a voter, but only if that voter has not voted |

## How it works

- **One shared database object.** `main.py` creates a single `Database` object and passes it to every other class, so only one place talks to the database.
- **Hosted MySQL database.** The data is stored in a MySQL database hosted online (Aiven). Connection details are read from a `.env` file, so no password is stored in the code.
- **Secret ballot.** The program stores only *whether* a voter has voted and each candidate's *total*. No record links a voter to the candidate they chose.
- **One vote per voter.** The voting step checks the voter ID and PIN, and the database refuses a second vote from the same voter.
- **Two counts for the audit.** Each candidate has a results count and an audit count that are updated together when a vote is cast. If someone edits one without the other, the audit shows NO MATCH for that candidate and does not reveal any voter's identity.
- **Safe removal.** A voter who has already voted cannot be removed, so the audit stays consistent.
- **PINs are stored hashed.** The database keeps a SHA-256 hash of the voter ID and PIN together, never the PIN itself.

### Architecture

```
Keyboard (menu input)
 |
 v
 Python code: Menu -> AdminService / VotingService / Audit
 |
 v
 Database class (MySQL)
```

## Project structure

```
secureballot/
├── main.py            Starts the application
├── menus.py           Main menu loop (class Menu)
├── database.py        All database code (class Database)
├── validation.py      Input checks (menu numbers, voter ID, 4-digit PIN)
├── models.py          Classes: Voter, Candidate, Admin
├── admin.py           Register voter, remove voter (class AdminService)
├── voting.py          The voting flow (class VotingService)
├── how_to_vote.py     "How to vote" instruction pages
├── audit.py           Results and audit screens (class Audit)
├── demo_tools.py      Demo helpers: tamper with one count, or reset all votes
├── tamper_demo.py     Scripted tampering demo (audit before, during and after)
├── .env.example       Template for your database settings
├── tests/             Unit tests, one file per module
│   ├── __init__.py
│   ├── test_menus.py
│   ├── test_database.py
│   ├── test_admin.py
│   ├── test_voting.py
│   ├── test_audit.py
│   └── test_models.py
├── .gitignore
└── README.md
```

## Requirements

- **Python 3** (tested with Python 3.14)
- **A MySQL database.** Our team database is hosted on Aiven. Ask the team for the connection details.
- **Two Python libraries:** `mysql-connector-python` (connects to MySQL) and `python-dotenv` (reads the `.env` file)

## Setup and installation

1. **Clone the repository**

   ```
   git clone <repository-URL>
   cd Secureballot
   ```

2. **Install the Python libraries**

   ```
   pip install mysql-connector-python python-dotenv
   ```

   Install both. Without `python-dotenv` the `.env` file is ignored and the database login fails.

3. **Create your settings file** by copying the template. Leave `.env.example` unchanged.

   Windows:

   ```
   copy .env.example .env
   ```

   macOS or Linux:

   ```
   cp .env.example .env
   ```

4. **Open `.env` and replace the placeholder values with the details the team sent you.** The settings are:

   | Setting | Meaning |
   |---|---|
   | `DB_HOST` | Database server address |
   | `DB_PORT` | Database server port |
   | `DB_USER` | Database username |
   | `DB_PASSWORD` | Database password |
   | `DB_NAME` | Name of the database |
   | `ADMIN_CODE` | Registration officer code (optional, `ADMIN123` if left out) |

   Never put real details in `.env.example`, and never commit `.env`; it is listed in `.gitignore`.

5. **Run the application.** On the first run, the program creates the tables and the sample data automatically. You don't need to run any SQL by hand.

### Keeping the database login secure

- **`.env.example`** is a template. It lists every setting the app needs, with placeholder values and no secrets. It is committed to the repository.
- **`.env`** is your private copy with the real database host, username and password. It stays on your own computer. It is listed in `.gitignore`, so git never tracks it, and it must never be committed or pasted into the README, the report or a chat.
- The real connection details are shared with team members and the facilitator privately, not through the repository.
- `database.py` reads these settings from the environment, so no password is written in the code.
- If `.env` is ever committed by mistake, deleting the file is not enough, because the password stays in the git history. Change the database password in Aiven and share the new one privately.

## Running the application

From the project folder:

```
python main.py
```

On some systems the command is `python3 main.py` or `py main.py`.

### Example session

```
WELCOME TO SECUREBALLOT
What would you like to do today?
1. Register voter
2. Vote
3. View results
4. Audit
5. How to vote
0. Exit
Type a number (0-5) and press Enter: 0
Goodbye.
```

To try the full journey: register a voter (option 1, using the admin code), vote as that voter (option 2), then check the results (option 3) and the audit (option 4).

## Sample data

The program loads this data on the first run, only when the tables are empty.

| Item | Value |
|---|---|
| Election name | SAMPLE PRESIDENTIAL ELECTION |
| Candidates | Candidate A, Candidate B, Candidate C |
| Sample voters (ID / PIN) | V001 / 1234, V002 / 4321, V003 / 1111 |
| Default admin code | ADMIN123 (can be changed with the ADMIN_CODE setting) |

All names, IDs and codes are fake. No real voter or election data is used.

## Running the tests

Run all tests from the project folder:

```
python -m unittest discover -v
```

The database tests connect with the same settings as the application (from `.env`). Each test creates its own temporary database (named `secureballot_test_` followed by random characters) and deletes it afterwards, so the tests never change your real data. The database user therefore needs permission to create and drop databases.

## Demo: simulating tampering

Two scripts show that the audit catches tampering. Neither is called from any menu.

- `python tamper_demo.py` runs the full demo: a normal election, then a hand-edited count for Candidate B, then the audit showing NO MATCH, then a reset.
- `python demo_tools.py` is a small menu to tamper with one candidate's vote count, or to reset all votes.

**Warning:** both scripts change the real data in the database. `tamper_demo.py` adds demo voters (DEMO001 onwards), and resetting sets every count to 0 and lets every voter vote again. Run them only on a demo database.

## Input validation and error handling

The application is designed not to crash on wrong input:

- Letters or symbols where a number is expected give a clear message, and the program asks again.
- A number outside the menu range is rejected.
- Voter IDs should be letters and digits only (for example `V001`), and the voting screen rejects anything else. A PIN must be exactly 4 digits.
- A voter ID that is not registered or a wrong PIN gives a clear error message, and the database refuses a second vote from the same voter.
- A wrong admin code is rejected.
- A duplicate voter ID cannot be registered.
- A voter who has already voted cannot be removed.
- Pressing Ctrl+C ends the session politely instead of showing an error.

## Limitations

SecureBallot is a classroom prototype, not a secure election system.

- The USSD code is **simulated** in the terminal. A real short code needs a mobile network operator.
- All data is **fake**, and the app handles **one sample election** at a time.
- It is **text only** and in **English only**.
- It is not secure enough for a real election.
- The app saves **totals**, not each vote separately, so a result cannot be recounted.
- The audit would not notice if someone changed both a candidate's two counts and the voter records so that they still agree.
- The program does not save who a voter chose, but it briefly handles both the voter and the choice while a vote is recorded, so secrecy cannot be guaranteed if someone controls the code.
- A 4-digit PIN has only 10,000 possible values, so even hashed PINs could be guessed quickly.
- The default admin code is a fixed example code.

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `Can't connect to MySQL server` | Check the host and port in `.env`, and that the Aiven database service is running. |
| `Access denied for user` | The `.env` file is missing or has wrong details, or `python-dotenv` is not installed. Check `.env` and run the `pip install` command from the setup steps. |
| `ModuleNotFoundError` | A library is not installed. Run the `pip install` command from the setup steps. |
| `python` is not recognized | Try `py main.py` (Windows) or `python3 main.py`. |
| Tests fail to import modules | Run them from the project folder with `python -m unittest discover -v`. |

## Team and contributions

| Team member | GitHub | Role | Files |
|---|---|---|---|
| Gold Adaobi Cole-Okafor | gold-coleokafor | Team lead and integration | `main.py`, `menus.py`, `.gitignore`, `tests/test_menus.py` |
| Cecilia Ndawi | cndawi | Database | `database.py`, `validation.py`, `demo_tools.py`, `tests/test_database.py` |
| Nyamesomfo Ama Osei-Nimako | noseinimak-dev | Registration and admin | `admin.py`, `README.md`, `tests/test_admin.py` |
| Irumva Laurette | ilaurette-creator | Voting | `voting.py`, `how_to_vote.py`, `tests/test_voting.py` |
| Leslie Gaju Ntihemuka | gajuleslie | Results and audit | `audit.py`, `tamper_demo.py`, `tests/test_audit.py` |
| Benjamin Semakula | bsemakula-blip | Models and demo | `models.py`, `tests/test_models.py` |
