from flask import Flask, redirect, render_template, url_for, request, g, session
from database import connect_to_database, getDatabase
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'flaskapp_db'):
        g.flaskapp_db.close()

def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from users where name = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route("/")
def index():
    user = get_current_user()
    db = getDatabase()
    question_cursor = db.execute("select questions.id, questions.question_text, askers.name as asker_name, teachers.name as teacher_name from questions join users as askers on askers.id = questions.asked_by_id join users as teachers on teachers.id = questions.teacher_id where questions.answer_text is not null")
    question_result = question_cursor.fetchall()
    return render_template("home.html", user = user, questions = question_result)

@app.route("/login", methods = ['POST', 'GET'])
def login():
    user = get_current_user()
    error = None
    if request.method == 'POST':
        db = getDatabase()
        name = request.form['name']
        password = request.form['password']
        fetchedperson_cursor = db.execute("select * from users where name = ?", [name])
        personfromdatabase = fetchedperson_cursor.fetchone()
        if personfromdatabase:
            if check_password_hash(personfromdatabase['password'], password):
                session['user'] = personfromdatabase['name']
                return redirect(url_for('index'))
            else:
                error = "Username or password did not match. Try again."
                # return render_template('login.html', error = error)
        else:
            error = "Username or password did not match. Try again."
            # return redirect(url_for('login'))

    return render_template("login.html", user = user, error = error)

@app.route("/register", methods = ["POST", "GET"])
def register():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = getDatabase()
        name = request.form["name"]
        password = request.form["password"]
        user_fetcing_cursor = db.execute("select * from users where name = ?", [name])
        existing_user  = user_fetcing_cursor.fetchone()
        if existing_user:
            error = "Username already taken, please choose a different username."
            return render_template("register.html", error = error)
        hashed_password = generate_password_hash(password)
        db.execute("insert into users (name, password, teacher, admin) values (?,?,?,?)",
                    [name, hashed_password, '0', '0'])
        db.commit()
        session['user'] = name
        return redirect(url_for('index'))
    return render_template("register.html", user = user)

@app.route('/askquestions', methods = ["POST", "GET"])
def askquestions():
    user = get_current_user()
    db = getDatabase()
    if request.method == "POST":
        question = request.form['question']
        teacher = request.form['teacher']
        db.execute("insert into questions (question_text, asked_by_id, teacher_id) values (?,?,?)", 
                   [question, user['id'], teacher])
        db.commit()
        return redirect(url_for("index"))
    teacher_cursor = db.execute("select * from users where teacher = 1")
    allteachers = teacher_cursor.fetchall()
    return render_template("askquestions.html", user = user, allteachers = allteachers)

@app.route('/unansweredquestions')
def unansweredquestions():
    user = get_current_user()
    db = getDatabase()
    question_cursor = db.execute("select questions.id, questions.question_text, users.name from questions join users on users.id = questions.asked_by_id where questions.answer_text is null and questions.teacher_id = ?",
                                  [user['id']])
    allquestions = question_cursor.fetchall()
    return render_template("unansweredquestions.html", user = user, allquestions = allquestions)

@app.route('/answerquestion/<question_id>', methods = ["POST", "GET"])
def answerquestion(question_id):
    user = get_current_user()
    db = getDatabase()
    if request.method == "POST":
        db.execute("update questions set answer_text = ? where id = ?", [request.form['answer'], question_id])
        db.commit()
        return redirect('unansweredquestions')
    question_cursor = db.execute("select id, question_text from questions where id = ?", [question_id])
    question = question_cursor.fetchone()
    return render_template("answerquestion.html", user = user, question = question)

@app.route('/allusers', methods = ["POST", "GET"])
def allusers():
    user = get_current_user()
    db = getDatabase()
    user_cursor = db.execute("select * from users")
    allusers = user_cursor.fetchall()
    return render_template("allusers.html", user = user, allusers = allusers)

@app.route('/promote/<int:id>', methods = ["POST", "GET"])
def promote(id):
    user = get_current_user()
    if request.method == "GET":
        db = getDatabase()
        db.execute("update users set teacher = 1 where id = ?", [id])
        db.commit() 
        return redirect(url_for('allusers'))
    return render_template("allusers.html", user = user)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)