import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "project.db"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
CREATE TABLE Sport(
    Sport_ID TEXT PRIMARY KEY,
    Sport_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL CHECK(Category IN ('Indoor','Outdoor','Water'))
);
""")

cursor.execute("""
CREATE TABLE Facility(
    Facility_ID INTEGER PRIMARY KEY,
    Facility_Name TEXT NOT NULL UNIQUE,
    Facility_Description TEXT NOT NULL,
    Status TEXT NOT NULL CHECK(Status IN ('Available','Maintenance','Closed'))
);
""")

cursor.execute("""
CREATE TABLE Member(
    Member_ID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Gender TEXT NOT NULL CHECK(Gender IN ('M','F')),
    Email TEXT NOT NULL UNIQUE,
    Phone_Number TEXT UNIQUE,
    Age INTEGER NOT NULL CHECK(Age > 0),
    DOB TEXT,
    Image BLOB
);
""")

cursor.execute("""
CREATE TABLE Administrator(
    Member_ID TEXT PRIMARY KEY,
    Administrator_ID INTEGER NOT NULL UNIQUE,
    Admin_Level INTEGER CHECK(Admin_Level BETWEEN 1 AND 5),
    Department TEXT,
    Office_Location TEXT,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Coach(
    Member_ID TEXT PRIMARY KEY,
    Coach_ID INTEGER NOT NULL UNIQUE,
    Sport_ID TEXT NOT NULL,
    Years_Experience INTEGER DEFAULT 0,
    Salary REAL DEFAULT 0.0,
    Joining_Date TEXT,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Player(
    Member_ID TEXT PRIMARY KEY,
    Roll_No INTEGER NOT NULL UNIQUE,
    Height REAL,
    Weight REAL,
    Blood_Group TEXT CHECK(Blood_Group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Team(
    Team_ID TEXT PRIMARY KEY,
    Team_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL,
    Sport_ID TEXT NOT NULL,
    Coach_ID INTEGER NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE,
    FOREIGN KEY(Coach_ID) REFERENCES Coach(Coach_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Team_Roster(
    Team_ID TEXT NOT NULL,
    Roll_No INTEGER NOT NULL,
    PRIMARY KEY(Team_ID, Roll_No),
    FOREIGN KEY(Team_ID) REFERENCES Team(Team_ID) ON DELETE CASCADE,
    FOREIGN KEY(Roll_No) REFERENCES Player(Roll_No) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Booking(
    Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Facility_ID INTEGER NOT NULL,
    Member_ID TEXT NOT NULL,
    Time_In TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d %H:%M:%S', Time_In) = Time_In),
    Time_Out TEXT
        CHECK(Time_Out IS NULL OR
              (strftime('%Y-%m-%d %H:%M:%S', Time_Out) = Time_Out
               AND Time_Out >= Time_In)),
    FOREIGN KEY(Facility_ID) REFERENCES Facility(Facility_ID) ON DELETE CASCADE,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Equipment(
    Equipment_ID TEXT PRIMARY KEY,
    Equipment_Name TEXT NOT NULL,
    Total_Qty INTEGER NOT NULL CHECK(Total_Qty >= 0),
    Status TEXT NOT NULL CHECK(Status IN ('Available','Damaged','Out of Stock')),
    Sport_ID TEXT NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Equipment_Loan(
    Member_ID TEXT NOT NULL,
    Equipment_ID TEXT NOT NULL,
    Quantity INTEGER NOT NULL CHECK(Quantity > 0),
    Issue_Time TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d %H:%M:%S', Issue_Time) = Issue_Time),
    Return_Time TEXT
        CHECK(Return_Time IS NULL OR
              (strftime('%Y-%m-%d %H:%M:%S', Return_Time) = Return_Time
               AND Return_Time >= Issue_Time)),
    PRIMARY KEY(Member_ID, Equipment_ID, Issue_Time),
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Equipment_ID) REFERENCES Equipment(Equipment_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Event(
    Event_ID TEXT PRIMARY KEY,
    Event_Name TEXT NOT NULL,
    Facility_ID INTEGER NOT NULL,
    Description TEXT NOT NULL,
    Start_Time TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d %H:%M:%S', Start_Time) = Start_Time),
    End_Time TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d %H:%M:%S', End_Time) = End_Time
              AND End_Time > Start_Time),
    Attendance_Status TEXT NOT NULL
        CHECK(Attendance_Status IN ('Completed','Cancelled','Postponed','Preponed')),
    FOREIGN KEY(Facility_ID) REFERENCES Facility(Facility_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Event_Team (
    Event_ID TEXT NOT NULL,
    Team_ID TEXT NOT NULL,
    PRIMARY KEY (Event_ID, Team_ID),
    FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID) ON DELETE CASCADE,
    FOREIGN KEY (Team_ID) REFERENCES Team(Team_ID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE Player_Stat(
    Member_ID TEXT NOT NULL,
    Event_ID TEXT,
    Metric_Name TEXT NOT NULL,
    Metric_Value TEXT NOT NULL,
    Recorded_Date TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d', Recorded_Date) = Recorded_Date),
    PRIMARY KEY(Member_ID, Metric_Name, Recorded_Date),
    FOREIGN KEY(Member_ID) REFERENCES Player(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Event_ID) REFERENCES Event(Event_ID) ON DELETE SET NULL
);
""")

cursor.execute("""
CREATE TABLE Complaint(
    Complaint_ID TEXT PRIMARY KEY,
    Raised_By TEXT NOT NULL,
    Description TEXT NOT NULL,
    Status TEXT NOT NULL CHECK(Status IN ('Open','Resolved')),
    Date_Filed TEXT NOT NULL DEFAULT (date('now')),
    Resolved_By TEXT,
    FOREIGN KEY(Raised_By) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY(Resolved_By) REFERENCES Administrator(Member_ID) ON DELETE SET NULL
);
""")

cursor.execute("""
CREATE TABLE Attendance(
    Member_ID TEXT NOT NULL,
    Session TEXT NOT NULL,
    Date TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d', Date) = Date),
    Status TEXT NOT NULL CHECK(Status IN ('Present','Absent')),
    FOREIGN KEY(Member_ID) REFERENCES Player(Member_ID) ON DELETE CASCADE
);
""")

conn.commit()
conn.close()

print("Schema synced successfully")
