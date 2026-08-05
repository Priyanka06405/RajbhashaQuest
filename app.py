from flask import Flask, render_template, request, redirect, session
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "RajbhashaQuest2026"

DATABASE = "database.db"


# -----------------------------
# Database Functions
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        score INTEGER DEFAULT 0,
        coins INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        answer TEXT,
        category TEXT
    )
    """)

    conn.commit()

    # Insert sample questions only if table is empty
    count = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    if count == 0:

        sample = [

            (
                "Computer का हिन्दी शब्द क्या है?",
                "संगणक",
                "पत्र",
                "बैठक",
                "कर्मचारी",
                "संगणक",
                "Rajbhasha"
            ),

            (
                "File का हिन्दी शब्द क्या है?",
                "संचिका",
                "पत्र",
                "सूची",
                "दस्तावेज",
                "संचिका",
                "Rajbhasha"
            ),

            (
                "Meeting का हिन्दी शब्द क्या है?",
                "बैठक",
                "कार्यालय",
                "रिपोर्ट",
                "अनुभाग",
                "बैठक",
                "Rajbhasha"
            ), 
            (
    "Office का हिन्दी शब्द क्या है?",
    "कार्यालय",
    "विद्यालय",
    "संगणक",
    "दस्तावेज",
    "कार्यालय",
    "Rajbhasha"
),

(
    "Department का हिन्दी शब्द क्या है?",
    "विभाग",
    "अनुभाग",
    "संचिका",
    "बैठक",
    "विभाग",
    "Rajbhasha"
),

(
    "Letter का हिन्दी शब्द क्या है?",
    "पत्र",
    "रिपोर्ट",
    "दस्तावेज",
    "संचिका",
    "पत्र",
    "Rajbhasha"
),

(
    "Document का हिन्दी शब्द क्या है?",
    "दस्तावेज",
    "पत्र",
    "बैठक",
    "विभाग",
    "दस्तावेज",
    "Rajbhasha"
),

(
    "Employee का हिन्दी शब्द क्या है?",
    "कर्मचारी",
    "अधिकारी",
    "अनुभाग",
    "कार्यालय",
    "कर्मचारी",
    "Rajbhasha"
),

(
    "Training का हिन्दी शब्द क्या है?",
    "प्रशिक्षण",
    "बैठक",
    "दस्तावेज",
    "रिपोर्ट",
    "प्रशिक्षण",
    "Rajbhasha"
),

(
    "Report का हिन्दी शब्द क्या है?",
    "प्रतिवेदन",
    "पत्र",
    "सूची",
    "दस्तावेज",
    "प्रतिवेदन",
    "Rajbhasha"
),

        ]

        cur.executemany("""
        INSERT INTO questions(
            question,
            option1,
            option2,
            option3,
            option4,
            answer,
            category
        )
        VALUES(?,?,?,?,?,?,?)
        """, sample)

        conn.commit()

    conn.close()


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        employee = request.form["employee"]
        name = request.form["name"]
        department = request.form["department"]

        conn = get_connection()

        player = conn.execute(
            "SELECT * FROM players WHERE employee_id=?",
            (employee,)
        ).fetchone()

        if player is None:

            conn.execute("""
            INSERT INTO players(
                employee_id,
                name,
                department
            )
            VALUES(?,?,?)
            """, (employee, name, department))

            conn.commit()

        conn.close()

        session["employee"] = employee
        session["name"] = name

        return redirect("/dashboard")

    return render_template("login.html")

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "employee" not in session:
        return redirect("/login")

    conn = get_connection()

    player = conn.execute(
        "SELECT * FROM players WHERE employee_id=?",
        (session["employee"],)
    ).fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        player=player
    )
# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# -----------------------------
# Quiz
# -----------------------------
@app.route("/quiz")
def quiz():

    if "employee" not in session:
        return redirect("/login")

    conn = get_connection()

    # First time starting the quiz
    if "quiz_questions" not in session:

        rows = conn.execute(
            "SELECT id FROM questions"
        ).fetchall()

        ids = [row["id"] for row in rows]

        random.shuffle(ids)

        # Take first 10 questions (or fewer if there aren't 10)
        session["quiz_questions"] = ids[:10]
        session["current_question"] = 0
        session["quiz_score"] = 0

    index = session["current_question"]

    # Quiz finished
    if index >= len(session["quiz_questions"]):

        final_score = session["quiz_score"]

        conn.execute("""
        UPDATE players
        SET score = score + ?
        WHERE employee_id = ?
        """, (final_score, session["employee"]))

        conn.commit()
        conn.close()

        session.pop("quiz_questions")
        session.pop("current_question")
        session.pop("quiz_score")

        return render_template(
            "result.html",
            message="🎉 Quiz Completed!",
            correct=f"Your Score: {final_score}"
        )

    question_id = session["quiz_questions"][index]

    question = conn.execute(
        "SELECT * FROM questions WHERE id=?",
        (question_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "quiz.html",
        question=question,
        current=index + 1,
        total=len(session["quiz_questions"])
    )
# -----------------------------
# Check Answer
# -----------------------------
@app.route("/check_answer", methods=["POST"])
def check_answer():

    if "employee" not in session:
        return redirect("/login")

    question_id = request.form["question_id"]
    selected = request.form["answer"]

    conn = get_connection()

    question = conn.execute(
        "SELECT * FROM questions WHERE id=?",
        (question_id,)
    ).fetchone()

    # Correct Answer
    if selected == question["answer"]:

        session["quiz_score"] += 10

        conn.execute("""
        UPDATE players
        SET
            xp = xp + 5,
            coins = coins + 2
        WHERE employee_id=?
        """, (session["employee"],))

        conn.commit()

    # Move to next question
    session["current_question"] += 1

    conn.close()

    return redirect("/quiz")
# -----------------------------
# Leaderboard
# -----------------------------
@app.route("/leaderboard")
def leaderboard():

    conn = get_connection()

    players = conn.execute("""
        SELECT *
        FROM players
        ORDER BY score DESC, xp DESC
    """).fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        players=players
    )
# -----------------------------
# Admin Login
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin/dashboard")

        return render_template(
            "admin_login.html",
            error="Invalid Username or Password"
        )

    return render_template("admin_login.html")


# -----------------------------
# Admin Dashboard
# -----------------------------
@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:

        return redirect("/admin")

    conn = get_connection()

    total_players = conn.execute(
        "SELECT COUNT(*) FROM players"
    ).fetchone()[0]

    total_questions = conn.execute(
        "SELECT COUNT(*) FROM questions"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        players=total_players,
        questions=total_questions
    )
# -----------------------------
# Question List
# -----------------------------
@app.route("/questions")
def questions():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()

    questions = conn.execute("""
        SELECT *
        FROM questions
        ORDER BY id
    """).fetchall()

    conn.close()

    return render_template(
        "questions.html",
        questions=questions
    )
# -----------------------------
# Add Question
# -----------------------------
@app.route("/add_question", methods=["GET", "POST"])
def add_question():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        question = request.form["question"]
        option1 = request.form["option1"]
        option2 = request.form["option2"]
        option3 = request.form["option3"]
        option4 = request.form["option4"]
        answer = request.form["answer"]
        category = request.form["category"]

        conn = get_connection()

        conn.execute("""
        INSERT INTO questions(
            question,
            option1,
            option2,
            option3,
            option4,
            answer,
            category
        )
        VALUES(?,?,?,?,?,?,?)
        """, (
            question,
            option1,
            option2,
            option3,
            option4,
            answer,
            category
        ))

        conn.commit()
        conn.close()

        return redirect("/questions")

    return render_template("add_question.html")
# -----------------------------
# Edit Question
# -----------------------------
@app.route("/edit_question/<int:id>", methods=["GET", "POST"])
def edit_question(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()

    if request.method == "POST":

        conn.execute("""
        UPDATE questions
        SET
            question=?,
            option1=?,
            option2=?,
            option3=?,
            option4=?,
            answer=?,
            category=?
        WHERE id=?
        """, (

            request.form["question"],
            request.form["option1"],
            request.form["option2"],
            request.form["option3"],
            request.form["option4"],
            request.form["answer"],
            request.form["category"],
            id

        ))

        conn.commit()
        conn.close()

        return redirect("/questions")

    question = conn.execute(
        "SELECT * FROM questions WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_question.html",
        question=question
    )
# -----------------------------
# Delete Question
# -----------------------------
@app.route("/delete_question/<int:id>")
def delete_question(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()

    conn.execute(
        "DELETE FROM questions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/questions")
# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)