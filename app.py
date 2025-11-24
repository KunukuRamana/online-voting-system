from flask import Flask, request, render_template, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey123"


# ---------------------------
# HOME PAGE
# ---------------------------
@app.route('/')
def home():
    return render_template("index.html")


# ---------------------------
# HTML PAGE ROUTES
# ---------------------------
@app.route('/admin_login_page')
def admin_login_page():
    return render_template("admin_login.html")


@app.route('/voter_login_page')
def voter_login_page():
    return render_template("voter_login.html")


@app.route('/create_election_page')
def create_election_page():
    return render_template("create_election.html")


@app.route('/add_candidate_page')
def add_candidate_page():
    return render_template("add_candidate.html")


@app.route('/results_page')
def results_page():

    conn = sqlite3.connect('voting.db')
    c = conn.cursor()

    c.execute("""
        SELECT candidates.id, candidates.name, COUNT(votes.id)
        FROM candidates 
        LEFT JOIN votes 
        ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
    """)
    results = c.fetchall()
    conn.close()

    max_votes = max([row[2] for row in results]) if results else 0

    return render_template("view_results.html",
                           results=results,
                           max_votes=max_votes)


# ---------------------------
# ADMIN LOGIN
# ---------------------------
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("""
        SELECT * FROM users WHERE username=? AND password=? AND role='admin'
    """, (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return render_template("admin_dashboard.html")
    else:
        return "Invalid Admin Login! <a href='/admin_login_page'>Try Again</a>"


# ---------------------------
# VOTER LOGIN
# ---------------------------
@app.route('/voter_login', methods=['POST'])
def voter_login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('voting.db')
    c = conn.cursor()

    # Check voter login
    c.execute("""
        SELECT * FROM users WHERE username=? AND password=? AND role='voter'
    """, (username, password))
    user = c.fetchone()

    if not user:
        conn.close()
        return "Invalid Voter Login! <a href='/voter_login_page'>Try Again</a>"

    # Check active election
    c.execute("SELECT id FROM elections WHERE status='Active'")
    active_election = c.fetchone()

    if not active_election:
        conn.close()
        return "No active election. Please wait for admin to start one."

    election_id = active_election[0]

    # Get candidates for active election
    c.execute("""
        SELECT id, name, position FROM candidates WHERE election_id=?
    """, (election_id,))
    candidates = c.fetchall()

    conn.close()

    # Save voter ID
    session['voter_id'] = user[0]

    return render_template("vote.html", candidates=candidates)


# ---------------------------
# SUBMIT VOTE
# ---------------------------
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    candidate_id = request.form['candidate']
    voter_id = session.get('voter_id')

    if not voter_id:
        return "Session expired! Please login again."

    conn = sqlite3.connect("voting.db")
    cur = conn.cursor()

    # Get active election
    cur.execute("SELECT id FROM elections WHERE status='Active'")
    active = cur.fetchone()

    if not active:
        conn.close()
        return "No active election."

    election_id = active[0]

    # Check if already voted
    cur.execute("""
        SELECT * FROM votes WHERE user_id=? AND election_id=?
    """, (voter_id, election_id))
    already_voted = cur.fetchone()

    if already_voted:
        conn.close()
        return "You already voted! <a href='/'>Back</a>"

    # Insert vote
    cur.execute("""
        INSERT INTO votes (user_id, candidate_id, election_id)
        VALUES (?, ?, ?)
    """, (voter_id, candidate_id, election_id))

    conn.commit()
    conn.close()

    return render_template("thankyou.html")


# ---------------------------
# START ELECTION
# ---------------------------
@app.route('/start_election', methods=['POST'])
def start_election():
    name = request.form['election_name']
    description = request.form['description']
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    conn = sqlite3.connect("voting.db")
    cur = conn.cursor()

    # Remove old elections
    cur.execute("DELETE FROM elections")

    # Insert new active election
    cur.execute("""
        INSERT INTO elections (name, description, start_time, end_time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, description, start_time, end_time, "Active"))

    conn.commit()
    conn.close()

    return redirect('/admin_login_page')


# ---------------------------
# ADD CANDIDATE (AUTO ACTIVE ELECTION)
# ---------------------------
@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    name = request.form['name']
    position = request.form['position']

    conn = sqlite3.connect("voting.db")
    cur = conn.cursor()

    # Get active election
    cur.execute("SELECT id FROM elections WHERE status='Active'")
    active = cur.fetchone()

    if not active:
        conn.close()
        return "No active election! Start an election first."

    election_id = active[0]

    # Insert candidate for active election
    cur.execute("""
        INSERT INTO candidates (name, position, election_id)
        VALUES (?, ?, ?)
    """, (name, position, election_id))

    conn.commit()
    conn.close()

    return "Candidate added! <a href='/admin_login_page'>Back</a>"


# ---------------------------
# MANAGE CANDIDATES
# ---------------------------
@app.route('/manage_candidates')
def manage_candidates():
    conn = sqlite3.connect("voting.db")
    cur = conn.cursor()

    cur.execute("SELECT id, name, position FROM candidates")
    candidates = cur.fetchall()

    conn.close()
    return render_template("manage_candidates.html", candidates=candidates)


# ---------------------------
# DELETE CANDIDATE
# ---------------------------
@app.route('/delete_candidate/<int:id>')
def delete_candidate(id):
    conn = sqlite3.connect("voting.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM candidates WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/manage_candidates')


# ---------------------------
# LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
