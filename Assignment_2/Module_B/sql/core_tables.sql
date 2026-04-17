-- ============================================================
-- Core system tables (separate from project-specific tables)
-- Handles: Authentication, Sessions, Audit Logging
-- ============================================================

CREATE TABLE IF NOT EXISTS UserLogin (
    User_ID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Member_ID     TEXT NOT NULL UNIQUE,
    Username      TEXT NOT NULL UNIQUE,
    Password_Hash TEXT NOT NULL,        -- SHA-256 hex digest
    Role          TEXT NOT NULL CHECK(Role IN ('admin','user')),
    Is_Active     INTEGER NOT NULL DEFAULT 1,
    Created_At    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS UserSession (
    Session_ID  INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID     INTEGER NOT NULL,
    Token       TEXT NOT NULL UNIQUE,
    Issued_At   TEXT NOT NULL DEFAULT (datetime('now')),
    Expires_At  TEXT NOT NULL,
    Is_Valid    INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (User_ID) REFERENCES UserLogin(User_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS AuditLog (
    Log_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
    Timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    Username    TEXT,
    Member_ID   TEXT,
    Role        TEXT,
    Action      TEXT NOT NULL,
    Table_Name  TEXT,
    Record_ID   TEXT,
    Details     TEXT,
    IP_Address  TEXT,
    Status      TEXT NOT NULL CHECK(Status IN ('SUCCESS','FAILURE','UNAUTHORIZED'))
);

-- ── Seed Users ────────────────────────────────────────────────
-- Passwords: admin123 -> 240be518...  |  user123 -> e606e38b...

INSERT OR IGNORE INTO UserLogin (Member_ID, Username, Password_Hash, Role) VALUES
-- Admins (M31-M40) → password: admin123
('M31','admin_rakesh', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin'),
('M32','admin_pooja',  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin'),
('M33','admin_suresh', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin'),
('M34','admin_anjali', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin'),
('M35','admin_vivek',  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin'),
-- Players (M01-M05) → password: user123
('M01','rahul_sharma', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
('M02','neha_singh',   'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
('M03','aman_verma',   'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
('M04','priya_mehta',  'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
('M05','rohan_das',    'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
-- Coaches → password: user123
('M21','coach_arvind', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user'),
('M22','coach_meena',  'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446','user');
