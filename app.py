from flask import Flask, redirect, render_template, url_for, request, g, session
from database import connect_to_database, getDatabase
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)


@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'flaskapp_db'):
        g.flaskapp_db.close()

def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = getDatabase()
        user_cursor = db.execute("select * from user where name = ?", [user])
        user_result = user_cursor.fetchone()
    return user_result

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        db = getDatabase()
        name = request.form["name"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method='sha256')

        db.execute("insert into users (name, password, teacher, admin) values (?,?,?,?)",
                    [name, hashed_password, '0', '0'])
        db.commit()
        return redirect(url_for('index'))

    return render_template("register.html")

@app.route("/logout")
def logout():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug = True)