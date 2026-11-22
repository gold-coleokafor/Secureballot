# Secureballot
 
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
| 1 | Register voter | An admin (registration officer) enters the admin code, then registers a voter with a voter ID and a 4-digit PIN chosen by the voter. The admin menu also lets the officer view voters and remove a voter who has not voted yet. |
| 2 | Vote | The voter picks a candidate, confirms, then enters their voter ID and PIN. Each voter can vote only once. |
| 3 | View results | Shows each candidate's total. Open to everyone, no PIN needed. |
| 4 | Audit | Compares each candidate's results count with a separately stored audit count (MATCH or NO MATCH), then checks that the total of all votes equals the number of voters who voted. Open to everyone. |
| 5 | How to vote | Short instruction pages for first-time voters. |
| 0 | Exit | Closes the application. |
 
On every sub-screen, **99** returns to the main menu and **0** exits.
 
### CRUD operations
 
| Operation | Where it happens |
|---|---|
| **Create** | Registering a voter |
| **Read** | Viewing results, the audit, and the list of voters |
| **Update** | Casting a vote updates the candidate's counts and marks the voter as having voted |
| **Delete** | The admin removes a voter, but only if that voter has not voted |
 
## How it works
 
- **One shared database object.** `main.py` creates a single `Database` object and passes it to every other class, so only one place talks to the database.
- **Hosted MySQL database.** The data is stored in a MySQL database hosted online (Aiven). Connection details are read from a `.env` file, so no password is stored in the code.

- 
