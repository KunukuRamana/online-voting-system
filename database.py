import sqlite3

conn = sqlite3.connect("voting.db")
cur = conn.cursor()

# USERS table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# ELECTIONS table (updated with new fields)
cur.execute("""
CREATE TABLE IF NOT EXISTS elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT
)
""")

# CANDIDATES table
cur.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    position TEXT,
    election_id INTEGER
)
""")

# VOTES table
cur.execute("""
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    candidate_id INTEGER,
    election_id INTEGER
)
""")

# Add default admin
cur.execute("SELECT * FROM users WHERE role='admin'")
if not cur.fetchone():
    cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("ramana", "ramana1747", "admin"))
    print("Default admin created")

# Add test voter
cur.execute("SELECT * FROM users WHERE username='voter1'")
if not cur.fetchone():
    cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("voter1", "voter123", "voter"))
    print("Test voter created")


voters = [
    ("voter2", "pass123", "voter"),
    ("voter3", "v123", "voter"),
    ("voter4", "abc123", "voter"),
    ("voter5", "ramu25", "voter")
]

for v in voters:
    cur.execute("SELECT * FROM users WHERE username=?", (v[0],))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", v)
        print(f"Voter created: {v[0]}")

conn.commit()
conn.close()

print("Database created successfully!")
