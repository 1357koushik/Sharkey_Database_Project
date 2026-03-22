BEGIN TRANSACTION;

CREATE TABLE Sport(
    Sport_ID TEXT PRIMARY KEY,
    Sport_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL CHECK(Category IN ('Indoor','Outdoor','Water'))
);
INSERT INTO "Sport" VALUES('S01','Football','Outdoor');
INSERT INTO "Sport" VALUES('S02','Basketball','Indoor');
INSERT INTO "Sport" VALUES('S03','Cricket','Outdoor');
INSERT INTO "Sport" VALUES('S04','Badminton','Indoor');
INSERT INTO "Sport" VALUES('S05','Tennis','Outdoor');
INSERT INTO "Sport" VALUES('S06','Volleyball','Outdoor');
INSERT INTO "Sport" VALUES('S07','Table Tennis','Indoor');
INSERT INTO "Sport" VALUES('S08','Athletics','Outdoor');
INSERT INTO "Sport" VALUES('S09','Swimming','Water');
INSERT INTO "Sport" VALUES('S10','Hockey','Outdoor');
INSERT INTO "Sport" VALUES('S11','Kabaddi','Indoor');
INSERT INTO "Sport" VALUES('S12','Chess','Indoor');
INSERT INTO "Sport" VALUES('S13','Baseball','Outdoor');
INSERT INTO "Sport" VALUES('S14','Handball','Indoor');
INSERT INTO "Sport" VALUES('S15','Rugby','Outdoor');
INSERT INTO "Sport" VALUES('S16','Boxing','Indoor');
INSERT INTO "Sport" VALUES('S17','Gymnastics','Indoor');
INSERT INTO "Sport" VALUES('S18','Skating','Outdoor');
INSERT INTO "Sport" VALUES('S19','Archery','Outdoor');
INSERT INTO "Sport" VALUES('S20','Cycling','Outdoor');

CREATE TABLE Facility(
    Facility_ID INTEGER PRIMARY KEY,
    Facility_Name TEXT NOT NULL UNIQUE,
    Facility_Description TEXT NOT NULL,
    Status TEXT NOT NULL CHECK(Status IN ('Available','Maintenance','Closed'))
);
INSERT INTO "Facility" VALUES(1,'Football Ground','105m x 68m FIFA standard grass field','Available');
INSERT INTO "Facility" VALUES(2,'Basketball Court','FIBA indoor wooden court with scoreboard','Available');
INSERT INTO "Facility" VALUES(3,'Cricket Stadium','Turf pitch with 70m boundary','Available');
INSERT INTO "Facility" VALUES(4,'Badminton Hall','BWF synthetic indoor courts','Available');
INSERT INTO "Facility" VALUES(5,'Tennis Court','ITF hard court surface','Available');
INSERT INTO "Facility" VALUES(6,'Volleyball Court','FIVB sand court','Available');
INSERT INTO "Facility" VALUES(7,'TT Arena','ITTF competition tables','Available');
INSERT INTO "Facility" VALUES(8,'Athletics Track','400m synthetic 8-lane track','Available');
INSERT INTO "Facility" VALUES(9,'Swimming Pool','50m Olympic size pool','Available');
INSERT INTO "Facility" VALUES(10,'Hockey Field','FIH certified artificial turf','Available');
INSERT INTO "Facility" VALUES(11,'Kabaddi Court','Indoor mat court','Available');
INSERT INTO "Facility" VALUES(12,'Chess Hall','FIDE rated tournament room','Available');
INSERT INTO "Facility" VALUES(13,'Baseball Field','90ft base path standard field','Available');
INSERT INTO "Facility" VALUES(14,'Handball Court','IHF indoor court','Available');
INSERT INTO "Facility" VALUES(15,'Rugby Ground','IRB regulation field','Available');
INSERT INTO "Facility" VALUES(16,'Boxing Ring','AIBA certified ring','Available');
INSERT INTO "Facility" VALUES(17,'Gymnastics Hall','FIG approved apparatus','Available');
INSERT INTO "Facility" VALUES(18,'Skating Track','200m outdoor track','Available');
INSERT INTO "Facility" VALUES(19,'Archery Range','70m outdoor range','Available');
INSERT INTO "Facility" VALUES(20,'Cycling Velodrome','250m indoor wooden track','Available');

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
INSERT INTO "Member" VALUES('M01','Rahul Sharma','M','user1@iitgn.ac.in','900000001',18,NULL,NULL);
INSERT INTO "Member" VALUES('M02','Neha Singh','F','user2@iitgn.ac.in','900000002',19,NULL,NULL);
INSERT INTO "Member" VALUES('M03','Aman Verma','M','user3@iitgn.ac.in','900000003',20,NULL,NULL);
INSERT INTO "Member" VALUES('M04','Priya Mehta','F','user4@iitgn.ac.in','900000004',21,NULL,NULL);
INSERT INTO "Member" VALUES('M05','Rohan Das','M','user5@iitgn.ac.in','900000005',22,NULL,NULL);
INSERT INTO "Member" VALUES('M06','Kavya Iyer','F','user6@iitgn.ac.in','900000006',23,NULL,NULL);
INSERT INTO "Member" VALUES('M07','Arjun Patel','M','user7@iitgn.ac.in','900000007',24,NULL,NULL);
INSERT INTO "Member" VALUES('M08','Sneha Rao','F','user8@iitgn.ac.in','900000008',25,NULL,NULL);
INSERT INTO "Member" VALUES('M09','Vikram Joshi','M','user9@iitgn.ac.in','900000009',26,NULL,NULL);
INSERT INTO "Member" VALUES('M10','Anjali Kapoor','F','user10@iitgn.ac.in','900000010',27,NULL,NULL);
INSERT INTO "Member" VALUES('M11','Ritesh Kumar','M','user11@iitgn.ac.in','900000011',28,NULL,NULL);
INSERT INTO "Member" VALUES('M12','Pooja Nair','F','user12@iitgn.ac.in','900000012',29,NULL,NULL);
INSERT INTO "Member" VALUES('M13','Sarthak Jain','M','user13@iitgn.ac.in','900000013',30,NULL,NULL);
INSERT INTO "Member" VALUES('M14','Ishita Gupta','F','user14@iitgn.ac.in','900000014',31,NULL,NULL);
INSERT INTO "Member" VALUES('M15','Manav Shah','M','user15@iitgn.ac.in','900000015',32,NULL,NULL);
INSERT INTO "Member" VALUES('M16','Simran Kaur','F','user16@iitgn.ac.in','900000016',33,NULL,NULL);
INSERT INTO "Member" VALUES('M17','Aditya Rao','M','user17@iitgn.ac.in','900000017',34,NULL,NULL);
INSERT INTO "Member" VALUES('M18','Tanvi Desai','F','user18@iitgn.ac.in','900000018',35,NULL,NULL);
INSERT INTO "Member" VALUES('M19','Yash Malhotra','M','user19@iitgn.ac.in','900000019',36,NULL,NULL);
INSERT INTO "Member" VALUES('M20','Meera Pillai','F','user20@iitgn.ac.in','900000020',37,NULL,NULL);
INSERT INTO "Member" VALUES('M21','Coach Arvind','M','user21@iitgn.ac.in','900000021',18,NULL,NULL);
INSERT INTO "Member" VALUES('M22','Coach Meena','F','user22@iitgn.ac.in','900000022',19,NULL,NULL);
INSERT INTO "Member" VALUES('M23','Coach Rakesh','M','user23@iitgn.ac.in','900000023',20,NULL,NULL);
INSERT INTO "Member" VALUES('M24','Coach Nitin','F','user24@iitgn.ac.in','900000024',21,NULL,NULL);
INSERT INTO "Member" VALUES('M25','Coach Kavita','M','user25@iitgn.ac.in','900000025',22,NULL,NULL);
INSERT INTO "Member" VALUES('M26','Coach Farhan','F','user26@iitgn.ac.in','900000026',23,NULL,NULL);
INSERT INTO "Member" VALUES('M27','Coach Dev','M','user27@iitgn.ac.in','900000027',24,NULL,NULL);
INSERT INTO "Member" VALUES('M28','Coach Sunil','F','user28@iitgn.ac.in','900000028',25,NULL,NULL);
INSERT INTO "Member" VALUES('M29','Coach Harsh','M','user29@iitgn.ac.in','900000029',26,NULL,NULL);
INSERT INTO "Member" VALUES('M30','Coach Divya','F','user30@iitgn.ac.in','900000030',27,NULL,NULL);
INSERT INTO "Member" VALUES('M31','Admin Rakesh','M','user31@iitgn.ac.in','900000031',28,NULL,NULL);
INSERT INTO "Member" VALUES('M32','Admin Pooja','F','user32@iitgn.ac.in','900000032',29,NULL,NULL);
INSERT INTO "Member" VALUES('M33','Admin Suresh','M','user33@iitgn.ac.in','900000033',30,NULL,NULL);
INSERT INTO "Member" VALUES('M34','Admin Anjali','F','user34@iitgn.ac.in','900000034',31,NULL,NULL);
INSERT INTO "Member" VALUES('M35','Admin Vivek','M','user35@iitgn.ac.in','900000035',32,NULL,NULL);
INSERT INTO "Member" VALUES('M36','Admin Megha','F','user36@iitgn.ac.in','900000036',33,NULL,NULL);
INSERT INTO "Member" VALUES('M37','Admin Deepak','M','user37@iitgn.ac.in','900000037',34,NULL,NULL);
INSERT INTO "Member" VALUES('M38','Admin Ritu','F','user38@iitgn.ac.in','900000038',35,NULL,NULL);
INSERT INTO "Member" VALUES('M39','Admin Karan','M','user39@iitgn.ac.in','900000039',36,NULL,NULL);
INSERT INTO "Member" VALUES('M40','Admin Aarti','F','user40@iitgn.ac.in','900000040',37,NULL,NULL);

CREATE TABLE Administrator(
    Member_ID TEXT PRIMARY KEY,
    Administrator_ID INTEGER NOT NULL UNIQUE,
    Admin_Level INTEGER CHECK(Admin_Level BETWEEN 1 AND 5),
    Department TEXT,
    Office_Location TEXT,
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Administrator" VALUES('M31',11,2,NULL,NULL);
INSERT INTO "Administrator" VALUES('M32',12,3,NULL,NULL);
INSERT INTO "Administrator" VALUES('M33',13,1,NULL,NULL);
INSERT INTO "Administrator" VALUES('M34',14,2,NULL,NULL);
INSERT INTO "Administrator" VALUES('M35',15,3,NULL,NULL);
INSERT INTO "Administrator" VALUES('M36',16,1,NULL,NULL);
INSERT INTO "Administrator" VALUES('M37',17,2,NULL,NULL);
INSERT INTO "Administrator" VALUES('M38',18,3,NULL,NULL);
INSERT INTO "Administrator" VALUES('M39',19,1,NULL,NULL);
INSERT INTO "Administrator" VALUES('M40',20,2,NULL,NULL);

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
INSERT into "Coach" VALUES('M21',1,'S01',0,0.0,NULL);
INSERT into "Coach" VALUES('M22',2,'S02',0,0.0,NULL);
INSERT into "Coach" VALUES('M23',3,'S03',0,0.0,NULL);
INSERT into "Coach" VALUES('M24',4,'S04',0,0.0,NULL);
INSERT into "Coach" VALUES('M25',5,'S05',0,0.0,NULL);
INSERT into "Coach" VALUES('M26',6,'S06',0,0.0,NULL);
INSERT into "Coach" VALUES('M27',7,'S07',0,0.0,NULL);
INSERT into "Coach" VALUES('M28',8,'S08',0,0.0,NULL);
INSERT into "Coach" VALUES('M29',9,'S09',0,0.0,NULL);
INSERT into "Coach" VALUES('M30',10,'S10',0,0.0,NULL);
INSERT into "Coach" VALUES('M31',11,'S11',0,0.0,NULL);
INSERT into "Coach" VALUES('M32',12,'S12',0,0.0,NULL);
INSERT into "Coach" VALUES('M33',13,'S13',0,0.0,NULL);
INSERT into "Coach" VALUES('M34',14,'S14',0,0.0,NULL);
INSERT into "Coach" VALUES('M35',15,'S15',0,0.0,NULL);
INSERT into "Coach" VALUES('M36',16,'S16',0,0.0,NULL);
INSERT into "Coach" VALUES('M37',17,'S17',0,0.0,NULL);
INSERT into "Coach" VALUES('M38',18,'S18',0,0.0,NULL);
INSERT into "Coach" VALUES('M39',19,'S19',0,0.0,NULL);
INSERT into "Coach" VALUES('M40',20,'S20',0,0.0,NULL);

CREATE TABLE Player(
    Member_ID TEXT PRIMARY KEY,
    Roll_No INTEGER NOT NULL UNIQUE,
    Height REAL,
    Weight REAL,
    Blood_Group TEXT CHECK(Blood_Group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Player" VALUES('M01',101,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M02',102,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M03',103,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M04',104,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M05',105,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M06',106,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M07',107,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M08',108,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M09',109,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M10',110,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M11',111,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M12',112,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M13',113,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M14',114,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M15',115,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M16',116,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M17',117,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M18',118,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M19',119,NULL,NULL,NULL);
INSERT INTO "Player" VALUES('M20',120,NULL,NULL,NULL);

CREATE TABLE Team(
    Team_ID TEXT PRIMARY KEY,
    Team_Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL,
    Sport_ID TEXT NOT NULL,
    Coach_ID INTEGER NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE,
    FOREIGN KEY(Coach_ID) REFERENCES Coach(Coach_ID) ON DELETE CASCADE
);
INSERT INTO "Team" VALUES('T01','Hallabol Football A','Hallabol','S01',1);
INSERT INTO "Team" VALUES('T02','Inter IIT Football Squad','Inter IIT','S01',2);
INSERT INTO "Team" VALUES('T03','Hallabol Basketball A','Hallabol','S02',3);
INSERT INTO "Team" VALUES('T04','Inter IIT Basketball Squad','Inter IIT','S02',4);
INSERT INTO "Team" VALUES('T05','Hallabol Cricket XI','Hallabol','S03',5);
INSERT INTO "Team" VALUES('T06','Inter IIT Cricket Squad','Inter IIT','S03',6);
INSERT INTO "Team" VALUES('T07','Hallabol Badminton','Hallabol','S04',7);
INSERT INTO "Team" VALUES('T08','Inter IIT Tennis Squad','Inter IIT','S05',8);
INSERT INTO "Team" VALUES('T09','Hallabol Volleyball','Hallabol','S06',9);
INSERT INTO "Team" VALUES('T10','Inter IIT TT Squad','Inter IIT','S07',10);
INSERT INTO "Team" VALUES('T11','Hallabol Athletics','Hallabol','S08',11);
INSERT INTO "Team" VALUES('T12','Inter IIT Swimming Squad','Inter IIT','S09',12);
INSERT INTO "Team" VALUES('T13','Hallabol Hockey','Hallabol','S10',13);
INSERT INTO "Team" VALUES('T14','Inter IIT Kabaddi Squad','Inter IIT','S11',14);
INSERT INTO "Team" VALUES('T15','Hallabol Chess','Hallabol','S12',15);
INSERT INTO "Team" VALUES('T16','Inter IIT Rugby Squad','Inter IIT','S15',16);
INSERT INTO "Team" VALUES('T17','Hallabol Boxing','Hallabol','S16',17);
INSERT INTO "Team" VALUES('T18','Inter IIT Gymnastics Squad','Inter IIT','S17',18);
INSERT INTO "Team" VALUES('T19','Hallabol Archery','Hallabol','S19',19);
INSERT INTO "Team" VALUES('T20','Inter IIT Cycling Squad','Inter IIT','S20',20);

CREATE TABLE Team_Roster(
    Team_ID TEXT NOT NULL,
    Roll_No INTEGER NOT NULL,
    PRIMARY KEY(Team_ID, Roll_No),
    FOREIGN KEY(Team_ID) REFERENCES Team(Team_ID) ON DELETE CASCADE,
    FOREIGN KEY(Roll_No) REFERENCES Player(Roll_No) ON DELETE CASCADE
);
INSERT INTO "Team_Roster" VALUES('T01',101);
INSERT INTO "Team_Roster" VALUES('T02',102);
INSERT INTO "Team_Roster" VALUES('T03',103);
INSERT INTO "Team_Roster" VALUES('T04',104);
INSERT INTO "Team_Roster" VALUES('T05',105);
INSERT INTO "Team_Roster" VALUES('T06',106);
INSERT INTO "Team_Roster" VALUES('T07',107);
INSERT INTO "Team_Roster" VALUES('T08',108);
INSERT INTO "Team_Roster" VALUES('T09',109);
INSERT INTO "Team_Roster" VALUES('T10',110);
INSERT INTO "Team_Roster" VALUES('T11',111);
INSERT INTO "Team_Roster" VALUES('T12',112);
INSERT INTO "Team_Roster" VALUES('T13',113);
INSERT INTO "Team_Roster" VALUES('T14',114);
INSERT INTO "Team_Roster" VALUES('T15',115);
INSERT INTO "Team_Roster" VALUES('T16',116);
INSERT INTO "Team_Roster" VALUES('T17',117);
INSERT INTO "Team_Roster" VALUES('T18',118);
INSERT INTO "Team_Roster" VALUES('T19',119);
INSERT INTO "Team_Roster" VALUES('T20',120);

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
INSERT INTO "Booking" VALUES(1,1,'M01','2026-02-01 13:30:00',NULL);
INSERT INTO "Booking" VALUES(2,2,'M02','2026-02-02 14:30:00','2026-02-02 17:30:00');
INSERT INTO "Booking" VALUES(3,3,'M03','2026-02-03 15:30:00','2026-02-03 17:30:00');
INSERT INTO "Booking" VALUES(4,4,'M04','2026-02-04 13:30:00','2026-02-04 16:30:00');
INSERT INTO "Booking" VALUES(5,5,'M05','2026-02-05 14:30:00','2026-02-05 16:30:00');
INSERT INTO "Booking" VALUES(6,6,'M06','2026-02-06 15:30:00','2026-02-06 18:30:00');
INSERT INTO "Booking" VALUES(7,7,'M07','2026-02-07 13:30:00',NULL);
INSERT INTO "Booking" VALUES(8,8,'M08','2026-02-08 14:30:00','2026-02-08 17:30:00');
INSERT INTO "Booking" VALUES(9,9,'M09','2026-02-09 15:30:00','2026-02-09 17:30:00');
INSERT INTO "Booking" VALUES(10,10,'M10','2026-02-10 13:30:00','2026-02-10 16:30:00');
INSERT INTO "Booking" VALUES(11,11,'M11','2026-02-11 14:30:00','2026-02-11 16:30:00');
INSERT INTO "Booking" VALUES(12,12,'M12','2026-02-12 15:30:00','2026-02-12 18:30:00');
INSERT INTO "Booking" VALUES(13,13,'M13','2026-02-13 13:30:00',NULL);
INSERT INTO "Booking" VALUES(14,14,'M14','2026-02-14 14:30:00','2026-02-14 17:30:00');
INSERT INTO "Booking" VALUES(15,15,'M15','2026-02-15 15:30:00','2026-02-15 17:30:00');
INSERT INTO "Booking" VALUES(16,16,'M16','2026-02-16 13:30:00','2026-02-16 16:30:00');
INSERT INTO "Booking" VALUES(17,17,'M17','2026-02-17 14:30:00','2026-02-17 16:30:00');
INSERT INTO "Booking" VALUES(18,18,'M18','2026-02-18 15:30:00','2026-02-18 18:30:00');
INSERT INTO "Booking" VALUES(19,19,'M19','2026-02-19 13:30:00',NULL);
INSERT INTO "Booking" VALUES(20,20,'M20','2026-02-20 14:30:00','2026-02-20 17:30:00');

CREATE TABLE Equipment(
    Equipment_ID TEXT PRIMARY KEY,
    Equipment_Name TEXT NOT NULL,
    Total_Qty INTEGER NOT NULL CHECK(Total_Qty >= 0),
    Status TEXT NOT NULL CHECK(Status IN ('Available','Damaged','Out of Stock')),
    Sport_ID TEXT NOT NULL,
    FOREIGN KEY(Sport_ID) REFERENCES Sport(Sport_ID) ON DELETE CASCADE
);
INSERT INTO "Equipment" VALUES('E01','Football',30,'Available','S01');
INSERT INTO "Equipment" VALUES('E02','Basketball',25,'Available','S02');
INSERT INTO "Equipment" VALUES('E03','Cricket Bat',40,'Available','S03');
INSERT INTO "Equipment" VALUES('E04','Badminton Racket',50,'Available','S04');
INSERT INTO "Equipment" VALUES('E05','Tennis Racket',30,'Available','S05');
INSERT INTO "Equipment" VALUES('E06','Volleyball',20,'Available','S06');
INSERT INTO "Equipment" VALUES('E07','TT Paddle',40,'Available','S07');
INSERT INTO "Equipment" VALUES('E08','Starting Blocks',10,'Available','S08');
INSERT INTO "Equipment" VALUES('E09','Swimming Kickboard',35,'Available','S09');
INSERT INTO "Equipment" VALUES('E10','Hockey Stick',45,'Available','S10');
INSERT INTO "Equipment" VALUES('E11','Kabaddi Mat',15,'Available','S11');
INSERT INTO "Equipment" VALUES('E12','Chess Board',25,'Available','S12');
INSERT INTO "Equipment" VALUES('E13','Baseball Bat',30,'Available','S13');
INSERT INTO "Equipment" VALUES('E14','Handball',20,'Available','S14');
INSERT INTO "Equipment" VALUES('E15','Rugby Ball',18,'Available','S15');
INSERT INTO "Equipment" VALUES('E16','Boxing Gloves',40,'Available','S16');
INSERT INTO "Equipment" VALUES('E17','Gymnastics Mat',25,'Available','S17');
INSERT INTO "Equipment" VALUES('E18','Skating Helmet',30,'Available','S18');
INSERT INTO "Equipment" VALUES('E19','Archery Bow',15,'Available','S19');
INSERT INTO "Equipment" VALUES('E20','Cycling Helmet',35,'Available','S20');

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
INSERT INTO "Equipment_Loan" VALUES('M01','E01',1,'2026-02-01 07:30:00',NULL);
INSERT INTO "Equipment_Loan" VALUES('M02','E02',2,'2026-02-02 09:30:00','2026-02-02 11:30:00');
INSERT INTO "Equipment_Loan" VALUES('M03','E03',1,'2026-02-03 11:30:00','2026-02-03 13:30:00');
INSERT INTO "Equipment_Loan" VALUES('M04','E04',2,'2026-02-04 13:30:00','2026-02-06 14:30:00');
INSERT INTO "Equipment_Loan" VALUES('M05','E05',1,'2026-02-05 07:30:00','2026-02-05 09:30:00');
INSERT INTO "Equipment_Loan" VALUES('M06','E06',2,'2026-02-06 09:30:00',NULL);
INSERT INTO "Equipment_Loan" VALUES('M07','E07',1,'2026-02-07 11:30:00','2026-02-09 12:30:00');
INSERT INTO "Equipment_Loan" VALUES('M08','E08',2,'2026-02-08 13:30:00','2026-02-08 15:30:00');
INSERT INTO "Equipment_Loan" VALUES('M09','E09',1,'2026-02-09 07:30:00','2026-02-09 09:30:00');
INSERT INTO "Equipment_Loan" VALUES('M10','E10',2,'2026-02-10 09:30:00','2026-02-12 10:30:00');
INSERT INTO "Equipment_Loan" VALUES('M11','E11',1,'2026-02-11 11:30:00',NULL);
INSERT INTO "Equipment_Loan" VALUES('M12','E12',2,'2026-02-12 13:30:00','2026-02-12 15:30:00');
INSERT INTO "Equipment_Loan" VALUES('M13','E13',1,'2026-02-13 07:30:00','2026-02-15 08:30:00');
INSERT INTO "Equipment_Loan" VALUES('M14','E14',2,'2026-02-14 09:30:00','2026-02-14 11:30:00');
INSERT INTO "Equipment_Loan" VALUES('M15','E15',1,'2026-02-15 11:30:00','2026-02-15 13:30:00');
INSERT INTO "Equipment_Loan" VALUES('M16','E16',2,'2026-02-16 13:30:00',NULL);
INSERT INTO "Equipment_Loan" VALUES('M17','E17',1,'2026-02-17 07:30:00','2026-02-17 09:30:00');
INSERT INTO "Equipment_Loan" VALUES('M18','E18',2,'2026-02-18 09:30:00','2026-02-18 11:30:00');
INSERT INTO "Equipment_Loan" VALUES('M19','E19',1,'2026-02-19 11:30:00','2026-02-21 12:30:00');
INSERT INTO "Equipment_Loan" VALUES('M20','E20',2,'2026-02-20 13:30:00','2026-02-20 15:30:00');

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
INSERT INTO "Event" VALUES('EV01','Hallabol Day 1',1,'Day 1 of Hallabol featuring major matches','2026-02-02 00:00:00','2026-02-02 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV02','Hallabol Day 2',2,'Day 2 of Hallabol featuring major matches','2026-02-03 00:00:00','2026-02-03 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV03','Hallabol Day 3',3,'Day 3 of Hallabol featuring major matches','2026-02-04 00:00:00','2026-02-04 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV04','Hallabol Day 4',4,'Day 4 of Hallabol featuring major matches','2026-02-05 00:00:00','2026-02-05 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV05','Hallabol Day 5',5,'Day 5 of Hallabol featuring major matches','2026-02-06 00:00:00','2026-02-06 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV06','Hallabol Day 6',6,'Day 6 of Hallabol featuring major matches','2026-02-07 00:00:00','2026-02-07 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV07','Hallabol Day 7',7,'Day 7 of Hallabol featuring major matches','2026-02-08 00:00:00','2026-02-08 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV08','Hallabol Day 8',8,'Day 8 of Hallabol featuring major matches','2026-02-09 00:00:00','2026-02-09 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV09','Hallabol Day 9',9,'Day 9 of Hallabol featuring major matches','2026-02-10 00:00:00','2026-02-10 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV10','Hallabol Day 10',10,'Day 10 of Hallabol featuring major matches','2026-02-11 00:00:00','2026-02-11 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV11','Hallabol Day 11',11,'Day 11 of Hallabol featuring major matches','2026-02-12 00:00:00','2026-02-12 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV12','Hallabol Day 12',12,'Day 12 of Hallabol featuring major matches','2026-02-13 00:00:00','2026-02-13 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV13','Hallabol Day 13',13,'Day 13 of Hallabol featuring major matches','2026-02-14 00:00:00','2026-02-14 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV14','Hallabol Day 14',14,'Day 14 of Hallabol featuring major matches','2026-02-15 00:00:00','2026-02-15 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV15','Hallabol Day 15',15,'Day 15 of Hallabol featuring major matches','2026-02-16 00:00:00','2026-02-16 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV16','Hallabol Day 16',16,'Day 16 of Hallabol featuring major matches','2026-02-17 00:00:00','2026-02-17 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV17','Hallabol Day 17',17,'Day 17 of Hallabol featuring major matches','2026-02-18 00:00:00','2026-02-18 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV18','Hallabol Day 18',18,'Day 18 of Hallabol featuring major matches','2026-02-19 00:00:00','2026-02-19 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV19','Hallabol Day 19',19,'Day 19 of Hallabol featuring major matches','2026-02-20 00:00:00','2026-02-20 03:00:00','Completed');
INSERT INTO "Event" VALUES('EV20','Hallabol Day 20',20,'Day 20 of Hallabol featuring major matches','2026-02-21 00:00:00','2026-02-21 03:00:00','Completed');

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
INSERT INTO "Player_Stat" VALUES('M01','EV01','100m Sprint','11.8 sec','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M02','EV02','Goals Scored','2','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M03',NULL,'Practice Runs','65','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M04','EV04','Smash Speed','280 km/h','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M05',NULL,'Net Practice Time','45 min','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M06','EV06','Aces','5','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M07','EV07','Blocks','3','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M08','EV08','Raid Points','7','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M09','EV09','200m Freestyle','1 min 58 sec','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M10',NULL,'Penalty Saves','1','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M11','EV11','Tackles','6','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M12','EV12','Checkmate Wins','4','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M13','EV13','Home Runs','1','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M14',NULL,'Handball Assists','3','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M15','EV15','Scrum Wins','5','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M16','EV16','Punch Accuracy','85%','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M17','EV17','Vault Score','9.1','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M18',NULL,'Lap Time','1 min 03 sec','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M19','EV19','Target Accuracy','90%','2026-02-01');
INSERT INTO "Player_Stat" VALUES('M20','EV20','Sprint Time','10.8 sec','2026-02-01');

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
INSERT INTO "Complaint" VALUES('C01','M01','Football goal net torn','Resolved','2026-02-01','M31');
INSERT INTO "Complaint" VALUES('C02','M02','Basketball scoreboard not working','Resolved','2026-02-01','M32');
INSERT INTO "Complaint" VALUES('C03','M03','Cricket pitch crack detected','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C04','M04','Pool tile crack near deep end','Resolved','2026-02-01','M33');
INSERT INTO "Complaint" VALUES('C05','M05','Badminton net sagging','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C06','M06','Tennis floodlight failure','Resolved','2026-02-01','M34');
INSERT INTO "Complaint" VALUES('C07','M07','Volleyball court sand uneven','Resolved','2026-02-01','M35');
INSERT INTO "Complaint" VALUES('C08','M08','TT table surface chipped','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C09','M09','Athletics lane marking faded','Resolved','2026-02-01','M36');
INSERT INTO "Complaint" VALUES('C10','M10','Hockey turf peeling','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C11','M11','Kabaddi mat torn','Resolved','2026-02-01','M37');
INSERT INTO "Complaint" VALUES('C12','M12','Chess hall AC failure','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C13','M13','Baseball mound erosion','Resolved','2026-02-01','M38');
INSERT INTO "Complaint" VALUES('C14','M14','Handball goalpost loose','Resolved','2026-02-01','M39');
INSERT INTO "Complaint" VALUES('C15','M15','Rugby ground waterlogging','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C16','M16','Boxing rope loose','Resolved','2026-02-01','M40');
INSERT INTO "Complaint" VALUES('C17','M17','Gymnastics beam padding worn','Open','2026-02-01',NULL);
INSERT INTO "Complaint" VALUES('C18','M18','Skating track surface crack','Resolved','2026-02-01','M31');
INSERT INTO "Complaint" VALUES('C19','M19','Archery stand unstable','Resolved','2026-02-01','M32');
INSERT INTO "Complaint" VALUES('C20','M20','Cycling track wooden panel lifted','Open','2026-02-01',NULL);

CREATE TABLE Attendance(
    Member_ID TEXT NOT NULL,
    Session TEXT NOT NULL,
    Date TEXT NOT NULL
        CHECK(strftime('%Y-%m-%d', Date) = Date),
    Status TEXT NOT NULL CHECK(Status IN ('Present','Absent')),
    FOREIGN KEY(Member_ID) REFERENCES Player(Member_ID) ON DELETE CASCADE
);
INSERT INTO "Attendance" VALUES('M01','PE Session','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M02','Inter IIT Practice','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M03','Hallabol Training','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M04','PE Session','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M05','Inter IIT Practice','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M06','Hallabol Training','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M07','PE Session','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M08','Inter IIT Practice','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M09','Hallabol Training','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M10','PE Session','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M11','Inter IIT Practice','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M12','Hallabol Training','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M13','PE Session','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M14','Inter IIT Practice','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M15','Hallabol Training','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M16','PE Session','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M17','Inter IIT Practice','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M18','Hallabol Training','2026-02-01','Absent');
INSERT INTO "Attendance" VALUES('M19','PE Session','2026-02-01','Present');
INSERT INTO "Attendance" VALUES('M20','Inter IIT Practice','2026-02-01','Absent');

DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('Booking',20);

CREATE TRIGGER prevent_booking_overlap
BEFORE INSERT ON Booking
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN EXISTS (
                SELECT 1 FROM Booking
                WHERE Facility_ID = NEW.Facility_ID
                AND NEW.Time_In < Time_Out
                AND (NEW.Time_Out IS NULL OR NEW.Time_Out > Time_In)
            )
            THEN RAISE(ABORT, 'Booking time overlaps with existing booking')
        END;
END;

COMMIT;
