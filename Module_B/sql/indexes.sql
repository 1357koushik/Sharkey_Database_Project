-- ============================================================
-- SQL INDEXES FOR PERFORMANCE OPTIMISATION
-- Module B - SubTask 4: SQL Indexing and Query Optimisation
-- ============================================================

-- 1. Member table: email and phone lookups (used in login & profile queries)
CREATE INDEX IF NOT EXISTS idx_member_email       ON Member(Email);
CREATE INDEX IF NOT EXISTS idx_member_phone       ON Member(Phone_Number);

-- 2. UserLogin: username lookup (used on every login)
CREATE INDEX IF NOT EXISTS idx_userlogin_username ON UserLogin(Username);
CREATE INDEX IF NOT EXISTS idx_userlogin_member   ON UserLogin(Member_ID);

-- 3. UserSession: token lookup (used on every authenticated request)
CREATE INDEX IF NOT EXISTS idx_session_token      ON UserSession(Token);
CREATE INDEX IF NOT EXISTS idx_session_user       ON UserSession(User_ID);
CREATE INDEX IF NOT EXISTS idx_session_valid      ON UserSession(Is_Valid, Expires_At);

-- 4. Booking: facility + time range queries (used for overlap checks & portfolio)
CREATE INDEX IF NOT EXISTS idx_booking_facility   ON Booking(Facility_ID);
CREATE INDEX IF NOT EXISTS idx_booking_member     ON Booking(Member_ID);
CREATE INDEX IF NOT EXISTS idx_booking_time_in    ON Booking(Time_In);
-- Composite: facility availability check (WHERE + range)
CREATE INDEX IF NOT EXISTS idx_booking_facility_time ON Booking(Facility_ID, Time_In, Time_Out);

-- 5. Equipment_Loan: member and equipment lookups
CREATE INDEX IF NOT EXISTS idx_loan_member        ON Equipment_Loan(Member_ID);
CREATE INDEX IF NOT EXISTS idx_loan_equipment     ON Equipment_Loan(Equipment_ID);
CREATE INDEX IF NOT EXISTS idx_loan_return        ON Equipment_Loan(Return_Time);

-- 6. Attendance: member + date queries
CREATE INDEX IF NOT EXISTS idx_attendance_member  ON Attendance(Member_ID);
CREATE INDEX IF NOT EXISTS idx_attendance_date    ON Attendance(Date);
-- Composite: member attendance by date range
CREATE INDEX IF NOT EXISTS idx_attendance_member_date ON Attendance(Member_ID, Date);

-- 7. Player_Stat: member + date range queries
CREATE INDEX IF NOT EXISTS idx_stat_member        ON Player_Stat(Member_ID);
CREATE INDEX IF NOT EXISTS idx_stat_date          ON Player_Stat(Recorded_Date);
CREATE INDEX IF NOT EXISTS idx_stat_event         ON Player_Stat(Event_ID);

-- 8. Complaint: raised_by and status filter
CREATE INDEX IF NOT EXISTS idx_complaint_raised   ON Complaint(Raised_By);
CREATE INDEX IF NOT EXISTS idx_complaint_status   ON Complaint(Status);
CREATE INDEX IF NOT EXISTS idx_complaint_resolved ON Complaint(Resolved_By);

-- 9. Coach: sport_id lookup
CREATE INDEX IF NOT EXISTS idx_coach_sport        ON Coach(Sport_ID);

-- 10. Team_Roster: roll_no lookup (join queries)
CREATE INDEX IF NOT EXISTS idx_roster_roll        ON Team_Roster(Roll_No);

-- 11. AuditLog: recent log queries
CREATE INDEX IF NOT EXISTS idx_audit_timestamp    ON AuditLog(Timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_member       ON AuditLog(Member_ID);
CREATE INDEX IF NOT EXISTS idx_audit_action       ON AuditLog(Action);
