import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("project.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# ---------------------------
# INSERT SPORTS (20 REAL)
# ---------------------------

sports = [
("S01","Football","Outdoor"),("S02","Basketball","Indoor"),
("S03","Cricket","Outdoor"),("S04","Badminton","Indoor"),
("S05","Tennis","Outdoor"),("S06","Volleyball","Outdoor"),
("S07","Table Tennis","Indoor"),("S08","Athletics","Outdoor"),
("S09","Swimming","Water"),("S10","Hockey","Outdoor"),
("S11","Kabaddi","Indoor"),("S12","Chess","Indoor"),
("S13","Baseball","Outdoor"),("S14","Handball","Indoor"),
("S15","Rugby","Outdoor"),("S16","Boxing","Indoor"),
("S17","Gymnastics","Indoor"),("S18","Skating","Outdoor"),
("S19","Archery","Outdoor"),("S20","Cycling","Outdoor")
]
cursor.executemany("INSERT INTO Sport VALUES (?,?,?)", sports)

# ---------------------------
# INSERT MEMBERS (40 REAL NAMES)
# ---------------------------

names = [
"Rahul Sharma","Neha Singh","Aman Verma","Priya Mehta","Rohan Das",
"Kavya Iyer","Arjun Patel","Sneha Rao","Vikram Joshi","Anjali Kapoor",
"Ritesh Kumar","Pooja Nair","Sarthak Jain","Ishita Gupta","Manav Shah",
"Simran Kaur","Aditya Rao","Tanvi Desai","Yash Malhotra","Meera Pillai",
"Coach Arvind","Coach Meena","Coach Rakesh","Coach Nitin","Coach Kavita",
"Coach Farhan","Coach Dev","Coach Sunil","Coach Harsh","Coach Divya",
"Admin Rakesh","Admin Pooja","Admin Suresh","Admin Anjali","Admin Vivek",
"Admin Megha","Admin Deepak","Admin Ritu","Admin Karan","Admin Aarti"
]

members=[]
for i in range(40):
    members.append((f"M{i+1:02d}",names[i],
                    "M" if i%2==0 else "F",
                    f"user{i+1}@iitgn.ac.in",
                    f"900000{i+1:03d}",
                    18+(i%20),
                    None))
cursor.executemany("INSERT INTO Member VALUES (?,?,?,?,?,?,?)", members)

# ---------------------------
# PLAYERS (20)
# ---------------------------
players=[(f"M{i:02d}",100+i) for i in range(1,21)]
cursor.executemany("INSERT INTO Player VALUES (?,?)", players)

# ---------------------------
# ADMINISTRATORS (10)
# ---------------------------
admins=[(f"M{i:02d}",i-20,1+(i%3)) for i in range(31,41)]
cursor.executemany("INSERT INTO Administrator VALUES (?,?,?)", admins)

# ---------------------------
# COACHES (20 one per sport)
# ---------------------------
coaches=[(f"M{i:02d}",i-20,f"S{i-20:02d}") for i in range(21,41)]
cursor.executemany("INSERT INTO Coach VALUES (?,?,?)", coaches)

# ---------------------------
# FACILITIES (20 REAL)
# ---------------------------
facilities=[
(1,"Football Ground","105m x 68m FIFA standard grass field","Available"),
(2,"Basketball Court","FIBA indoor wooden court with scoreboard","Available"),
(3,"Cricket Stadium","Turf pitch with 70m boundary","Available"),
(4,"Badminton Hall","BWF synthetic indoor courts","Available"),
(5,"Tennis Court","ITF hard court surface","Available"),
(6,"Volleyball Court","FIVB sand court","Available"),
(7,"TT Arena","ITTF competition tables","Available"),
(8,"Athletics Track","400m synthetic 8-lane track","Available"),
(9,"Swimming Pool","50m Olympic size pool","Available"),
(10,"Hockey Field","FIH certified artificial turf","Available"),
(11,"Kabaddi Court","Indoor mat court","Available"),
(12,"Chess Hall","FIDE rated tournament room","Available"),
(13,"Baseball Field","90ft base path standard field","Available"),
(14,"Handball Court","IHF indoor court","Available"),
(15,"Rugby Ground","IRB regulation field","Available"),
(16,"Boxing Ring","AIBA certified ring","Available"),
(17,"Gymnastics Hall","FIG approved apparatus","Available"),
(18,"Skating Track","200m outdoor track","Available"),
(19,"Archery Range","70m outdoor range","Available"),
(20,"Cycling Velodrome","250m indoor wooden track","Available")
]
cursor.executemany("INSERT INTO Facility VALUES (?,?,?,?)", facilities)

# ---------------------------
# TEAMS (20 REAL)
# ---------------------------
teams=[
("T01","Hallabol Football A","Hallabol","S01",1),
("T02","Inter IIT Football Squad","Inter IIT","S01",2),
("T03","Hallabol Basketball A","Hallabol","S02",3),
("T04","Inter IIT Basketball Squad","Inter IIT","S02",4),
("T05","Hallabol Cricket XI","Hallabol","S03",5),
("T06","Inter IIT Cricket Squad","Inter IIT","S03",6),
("T07","Hallabol Badminton","Hallabol","S04",7),
("T08","Inter IIT Tennis Squad","Inter IIT","S05",8),
("T09","Hallabol Volleyball","Hallabol","S06",9),
("T10","Inter IIT TT Squad","Inter IIT","S07",10),
("T11","Hallabol Athletics","Hallabol","S08",11),
("T12","Inter IIT Swimming Squad","Inter IIT","S09",12),
("T13","Hallabol Hockey","Hallabol","S10",13),
("T14","Inter IIT Kabaddi Squad","Inter IIT","S11",14),
("T15","Hallabol Chess","Hallabol","S12",15),
("T16","Inter IIT Rugby Squad","Inter IIT","S15",16),
("T17","Hallabol Boxing","Hallabol","S16",17),
("T18","Inter IIT Gymnastics Squad","Inter IIT","S17",18),
("T19","Hallabol Archery","Hallabol","S19",19),
("T20","Inter IIT Cycling Squad","Inter IIT","S20",20)
]
cursor.executemany("INSERT INTO Team VALUES (?,?,?,?,?)", teams)

# ---------------------------
# EQUIPMENT (20 REAL)
# ---------------------------
equipment=[
("E01","Football",30,"Available","S01"),
("E02","Basketball",25,"Available","S02"),
("E03","Cricket Bat",40,"Available","S03"),
("E04","Badminton Racket",50,"Available","S04"),
("E05","Tennis Racket",30,"Available","S05"),
("E06","Volleyball",20,"Available","S06"),
("E07","TT Paddle",40,"Available","S07"),
("E08","Starting Blocks",10,"Available","S08"),
("E09","Swimming Kickboard",35,"Available","S09"),
("E10","Hockey Stick",45,"Available","S10"),
("E11","Kabaddi Mat",15,"Available","S11"),
("E12","Chess Board",25,"Available","S12"),
("E13","Baseball Bat",30,"Available","S13"),
("E14","Handball",20,"Available","S14"),
("E15","Rugby Ball",18,"Available","S15"),
("E16","Boxing Gloves",40,"Available","S16"),
("E17","Gymnastics Mat",25,"Available","S17"),
("E18","Skating Helmet",30,"Available","S18"),
("E19","Archery Bow",15,"Available","S19"),
("E20","Cycling Helmet",35,"Available","S20")
]
cursor.executemany("INSERT INTO Equipment VALUES (?,?,?,?,?)", equipment)

# ---------------------------
# EVENTS (20 REAL)
# ---------------------------
base=datetime(2026,2,1)
events=[]
for i in range(1,21):
    start=base+timedelta(days=i)
    events.append((f"EV{i:02d}",
                   f"Hallabol Day {i}",
                   i,
                   f"Day {i} of Hallabol featuring major matches",
                   start.strftime("%Y-%m-%d %H:%M:%S"),
                   (start+timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
                   "Completed"))
cursor.executemany("INSERT INTO Event VALUES (?,?,?,?,?,?,?)", events)

# ---------------------------
# PLAYER STATS (20 REAL METRICS)
# ---------------------------
base_date = datetime(2026, 2, 1)

player_stats = [
("M01","EV01","100m Sprint","11.8 sec"),
("M02","EV02","Goals Scored","2"),
("M03",None,"Practice Runs","65"),
("M04","EV04","Smash Speed","280 km/h"),
("M05",None,"Net Practice Time","45 min"),
("M06","EV06","Aces","5"),
("M07","EV07","Blocks","3"),
("M08","EV08","Raid Points","7"),
("M09","EV09","200m Freestyle","1 min 58 sec"),
("M10",None,"Penalty Saves","1"),
("M11","EV11","Tackles","6"),
("M12","EV12","Checkmate Wins","4"),
("M13","EV13","Home Runs","1"),
("M14",None,"Handball Assists","3"),
("M15","EV15","Scrum Wins","5"),
("M16","EV16","Punch Accuracy","85%"),
("M17","EV17","Vault Score","9.1"),
("M18",None,"Lap Time","1 min 03 sec"),
("M19","EV19","Target Accuracy","90%"),
("M20","EV20","Sprint Time","10.8 sec")
]

stats_insert = []

for stat in player_stats:
    stats_insert.append((
        stat[0],          # Member_ID
        stat[1],          # Event_ID (nullable)
        stat[2],          # Metric_Name
        stat[3],          # Metric_Value
        base_date.strftime("%Y-%m-%d")
    ))

cursor.executemany("""
INSERT INTO Player_Stat
(Member_ID, Event_ID, Metric_Name, Metric_Value, Recorded_Date)
VALUES (?,?,?,?,?)
""", stats_insert)

# team roaster data

team_roster = []

for i in range(20):
    team_roster.append((
        f"T{i+1:02d}",     # Team_ID
        101 + i            # Roll_No (101–120)
    ))

cursor.executemany("""
INSERT INTO Team_Roster (Team_ID, Roll_No)
VALUES (?,?)
""", team_roster)


# ---------------------------
# COMPLAINTS (20 VARIED)
# ---------------------------
complaints=[
("C01","M01","Football goal net torn","Resolved","M31"),
("C02","M02","Basketball scoreboard not working","Resolved","M32"),
("C03","M03","Cricket pitch crack detected","Open",None),
("C04","M04","Pool tile crack near deep end","Resolved","M33"),
("C05","M05","Badminton net sagging","Open",None),
("C06","M06","Tennis floodlight failure","Resolved","M34"),
("C07","M07","Volleyball court sand uneven","Resolved","M35"),
("C08","M08","TT table surface chipped","Open",None),
("C09","M09","Athletics lane marking faded","Resolved","M36"),
("C10","M10","Hockey turf peeling","Open",None),
("C11","M11","Kabaddi mat torn","Resolved","M37"),
("C12","M12","Chess hall AC failure","Open",None),
("C13","M13","Baseball mound erosion","Resolved","M38"),
("C14","M14","Handball goalpost loose","Resolved","M39"),
("C15","M15","Rugby ground waterlogging","Open",None),
("C16","M16","Boxing rope loose","Resolved","M40"),
("C17","M17","Gymnastics beam padding worn","Open",None),
("C18","M18","Skating track surface crack","Resolved","M31"),
("C19","M19","Archery stand unstable","Resolved","M32"),
("C20","M20","Cycling track wooden panel lifted","Open",None)
]
cursor.executemany("INSERT INTO Complaint VALUES (?,?,?,?,?)", complaints)

# ---------------------------
# ATTENDANCE (20)
# ---------------------------
attendance=[]
sessions=["PE Session","Inter IIT Practice","Hallabol Training"]
for i in range(20):
    attendance.append((f"M{i+1:02d}",
                       sessions[i%3],
                       base.strftime("%Y-%m-%d"),
                       "Present" if i%2==0 else "Absent"))
cursor.executemany("INSERT INTO Attendance VALUES (?,?,?,?)", attendance)


base = datetime(2026, 2, 1, 7, 30, 0)

realistic_loans = []

for i in range(20):

    issue = base + timedelta(days=i, hours=(i % 4) * 2)
    
    # Some returned same day, some late, some not returned
    if i % 5 == 0:
        return_time = None  # Not yet returned
    elif i % 3 == 0:
        return_time = issue + timedelta(days=2, hours=1)  # Returned late
    else:
        return_time = issue + timedelta(hours=2)  # Normal return

    realistic_loans.append((
        f"M{i+1:02d}",               # Member_ID
        f"E{i+1:02d}",               # Equipment_ID
        1 + (i % 2),                 # Quantity 1 or 2
        issue.strftime("%Y-%m-%d %H:%M:%S"),
        None if return_time is None else return_time.strftime("%Y-%m-%d %H:%M:%S")
    ))

cursor.executemany("""
INSERT INTO Equipment_Loan
(Member_ID, Equipment_ID, Quantity, Issue_Time, Return_Time)
VALUES (?,?,?,?,?)
""", realistic_loans)

realistic_bookings = []

for i in range(20):

    time_in = base + timedelta(days=i, hours=6 + (i % 3))

    # Some sessions ongoing (no checkout yet)
    if i % 6 == 0:
        time_out = None
    else:
        time_out = time_in + timedelta(hours=2 + (i % 2))

    realistic_bookings.append((
        i + 1,                        # Facility_ID
        f"M{i+1:02d}",                 # Member_ID
        time_in.strftime("%Y-%m-%d %H:%M:%S"),
        None if time_out is None else time_out.strftime("%Y-%m-%d %H:%M:%S")
    ))

cursor.executemany("""
INSERT INTO Booking
(Facility_ID, Member_ID, Time_In, Time_Out)
VALUES (?,?,?,?)
""", realistic_bookings)


conn.commit()
conn.close()

print("✅ PROFESSIONAL DATABASE CREATED SUCCESSFULLY")
