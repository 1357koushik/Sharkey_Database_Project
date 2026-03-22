# Module B - Local API Development, RBAC, and Database Optimisation
## CS432 Databases - IIT Gandhinagar - 2025-2026

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Delete the old database if it exists
rm app/sports_club.db

# 3. Run the server from the app directory
cd app
python app.py

# 4. Open the UI
http://localhost:5000/ui
```

---

## Default Login Credentials

| Role  | Username     | Password |
|-------|--------------|----------|
| Admin | admin_rakesh | admin123 |
| Admin | admin_pooja  | admin123 |
| User  | rahul_sharma | user123  |
| User  | neha_singh   | user123  |
| Coach | coach_arvind | user123  |

---

## Project Structure

```
Module_B/
├── app/
│   ├── app.py              # Flask app entry point
│   ├── db.py               # DB init and connection helper
│   ├── auth_utils.py       # JWT creation, validation, decorators
│   ├── audit.py            # Audit logging to DB and file
│   ├── routes/
│   │   ├── auth.py         # POST /login, GET /isAuth, POST /logout
│   │   ├── members.py      # CRUD /members/, portfolio /members/portfolio/<id>
│   │   ├── players.py      # CRUD /players/
│   │   ├── coaches.py      # CRUD /coaches/
│   │   ├── teams.py        # CRUD /teams/, roster /teams/<id>/roster
│   │   ├── facilities.py   # GET/PUT /facilities/
│   │   ├── bookings.py     # CRUD /bookings/
│   │   ├── equipment.py    # CRUD /equipment/, loans /equipment/loans
│   │   ├── events.py       # CRUD /events/
│   │   ├── complaints.py   # CRUD /complaints/
│   │   ├── attendance.py   # GET/POST /attendance/
│   │   ├── stats.py        # CRUD /stats/
│   │   └── admin.py        # /admin/logs, /admin/benchmark, /admin/dashboard
│   ├── templates/
│   │   └── index.html      # SPA shell
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── api.js      # API fetch wrappers
│           └── app.js      # SPA router and all view renderers
├── sql/
│   ├── project_dump.sql    # Full schema and seed data
│   ├── core_tables.sql     # UserLogin, UserSession, AuditLog and seed users
│   └── indexes.sql         # All SQL indexes for performance
├── logs/
│   └── audit.log           # Auto-generated on first API call
├── report.ipynb            # Optimisation report and benchmarking
└── requirements.txt
```

---

## API Reference

### Authentication

| Method | Endpoint  | Description                    | Auth Required |
|--------|-----------|--------------------------------|---------------|
| POST   | /login    | Login and receive JWT token    | No            |
| GET    | /isAuth   | Check if current token is valid | Yes          |
| POST   | /logout   | Revoke current token           | Yes           |
| GET    | /         | Welcome message                | No            |

### Session Token

After login the server returns a JWT token. Pass it on every request as shown below.

```
Authorization: Bearer <your_token_here>
```

The token is valid for 8 hours. After that you need to log in again.

### Members

| Method | Endpoint                     | Description              | Auth Required |
|--------|------------------------------|--------------------------|---------------|
| GET    | /members/                    | List all members         | Yes           |
| GET    | /members/<id>                | Get single member        | Yes           |
| GET    | /members/portfolio/<id>      | Get full member portfolio | Yes          |
| POST   | /members/                    | Create new member        | Admin only    |
| PUT    | /members/<id>                | Update member            | Yes           |
| DELETE | /members/<id>                | Delete member            | Admin only    |

### Players

| Method | Endpoint          | Description       | Auth Required |
|--------|-------------------|-------------------|---------------|
| GET    | /players/         | List all players  | Yes           |
| POST   | /players/         | Add player record | Admin only    |
| DELETE | /players/<id>     | Remove player     | Admin only    |

### Coaches

| Method | Endpoint          | Description       | Auth Required |
|--------|-------------------|-------------------|---------------|
| GET    | /coaches/         | List all coaches  | Yes           |
| POST   | /coaches/         | Add coach record  | Admin only    |
| DELETE | /coaches/<id>     | Remove coach      | Admin only    |

### Teams

| Method | Endpoint               | Description        | Auth Required |
|--------|------------------------|--------------------|---------------|
| GET    | /teams/                | List all teams     | Yes           |
| GET    | /teams/<id>/roster     | Get team roster    | Yes           |
| POST   | /teams/                | Create team        | Admin only    |
| DELETE | /teams/<id>            | Delete team        | Admin only    |

### Bookings

| Method | Endpoint            | Description         | Auth Required |
|--------|---------------------|---------------------|---------------|
| GET    | /bookings/          | List bookings       | Yes           |
| POST   | /bookings/          | Create booking      | Yes           |
| PUT    | /bookings/<id>      | Update booking      | Yes           |
| DELETE | /bookings/<id>      | Delete booking      | Yes           |

### Equipment

| Method | Endpoint               | Description          | Auth Required |
|--------|------------------------|----------------------|---------------|
| GET    | /equipment/            | List all equipment   | Yes           |
| GET    | /equipment/loans       | List active loans    | Yes           |
| POST   | /equipment/loans       | Create loan          | Yes           |
| PUT    | /equipment/<id>        | Update equipment     | Admin only    |
| DELETE | /equipment/<id>        | Delete equipment     | Admin only    |

### Events

| Method | Endpoint         | Description      | Auth Required |
|--------|------------------|------------------|---------------|
| GET    | /events/         | List all events  | Yes           |
| POST   | /events/         | Create event     | Admin only    |
| PUT    | /events/<id>     | Update event     | Admin only    |
| DELETE | /events/<id>     | Delete event     | Admin only    |

### Complaints

| Method | Endpoint              | Description       | Auth Required        |
|--------|-----------------------|-------------------|----------------------|
| GET    | /complaints/          | List complaints   | Yes                  |
| POST   | /complaints/          | File complaint    | Yes                  |
| PUT    | /complaints/<id>      | Resolve complaint | Admin only           |
| DELETE | /complaints/<id>      | Delete complaint  | Admin only           |

### Attendance

| Method | Endpoint        | Description         | Auth Required |
|--------|-----------------|---------------------|---------------|
| GET    | /attendance/    | List attendance     | Yes           |
| POST   | /attendance/    | Mark attendance     | Admin only    |

### Player Stats

| Method | Endpoint                              | Description     | Auth Required |
|--------|---------------------------------------|-----------------|---------------|
| GET    | /stats/                               | List all stats  | Yes           |
| POST   | /stats/                               | Add stat record | Admin only    |
| PUT    | /stats/<id>/<metric>/<date>           | Update stat     | Admin only    |
| DELETE | /stats/<id>/<metric>/<date>           | Delete stat     | Admin only    |

### Admin

| Method | Endpoint            | Description                   | Auth Required |
|--------|---------------------|-------------------------------|---------------|
| GET    | /admin/logs         | View audit logs               | Admin only    |
| GET    | /admin/users        | List all system users         | Admin only    |
| POST   | /admin/users        | Create new login user         | Admin only    |
| DELETE | /admin/users/<id>   | Delete login user             | Admin only    |
| GET    | /admin/benchmark    | Run query benchmarks          | Admin only    |
| GET    | /admin/dashboard    | Summary stats for dashboard   | Admin only    |

---

## RBAC Summary

| Action                          | Admin | Regular User         |
|---------------------------------|-------|----------------------|
| View members list               | Yes   | No                   |
| View players list               | Yes   | No                   |
| View coaches list               | Yes   | No                   |
| View equipment list             | Yes   | No                   |
| View own portfolio              | Yes   | Yes                  |
| View another member portfolio   | Yes   | No                   |
| Create or delete any record     | Yes   | No                   |
| File a complaint                | Yes   | Yes                  |
| Resolve or delete complaint     | Yes   | No                   |
| View audit logs and benchmark   | Yes   | No                   |
| View teams, events, facilities  | Yes   | Yes                  |
| View own stats                  | Yes   | Yes (own only)       |

---

## SQL Indexes Applied

All indexes are defined in sql/indexes.sql and applied automatically when the server starts.

| Index Name                  | Table          | Columns                        | Purpose                        |
|-----------------------------|----------------|--------------------------------|--------------------------------|
| idx_userlogin_username      | UserLogin      | Username                       | Login lookup on every request  |
| idx_session_token           | UserSession    | Token                          | Token validation on every call |
| idx_booking_facility_time   | Booking        | Facility_ID, Time_In, Time_Out | Overlap check on new bookings  |
| idx_attendance_member_date  | Attendance     | Member_ID, Date                | Date range queries             |
| idx_complaint_status        | Complaint      | Status                         | Filter open and resolved       |
| idx_stat_member             | Player_Stat    | Member_ID                      | Portfolio stats load           |
| idx_audit_timestamp         | AuditLog       | Timestamp                      | Recent log queries             |
| idx_loan_member             | Equipment_Loan | Member_ID                      | Portfolio loan history         |
| idx_coach_sport             | Coach          | Sport_ID                       | Coach sport lookup             |
| idx_roster_roll             | Team_Roster    | Roll_No                        | Team roster join queries       |

---

## Security Features

- JWT Tokens: Signed with HS256, 8 hour expiry, user id and role embedded inside the token
- Password Hashing: SHA-256, no plaintext passwords stored anywhere
- Token Revocation: Logout adds the token to RevokedToken table so it cannot be reused
- RBAC: login_required and admin_required decorators applied on all 47 routes
- Audit Logging: Every data-modifying API call is logged to both AuditLog table and logs/audit.log
- Cascade Deletes: Deleting a Member automatically removes all related Player, Coach, Booking, Complaint and Attendance records

---

## Performance Benchmarking

Go to the UI, log in as admin, and click Benchmark in the sidebar.

Or call the endpoint directly after logging in:

```
GET /admin/benchmark
Authorization: Bearer <your_token>
```

This runs 500 iterations on 6 key queries and returns timing in milliseconds along with EXPLAIN QUERY PLAN output showing whether each query is using an index or doing a full table scan.

For a full before and after comparison with graphs, open report.ipynb in Jupyter and run all cells top to bottom.

---

## Requirements

```
flask>=3.0.0
PyJWT>=2.8.0
```


*CS432 Databases - Track 1 Assignment 2 - Module B*
