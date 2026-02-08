from flask import Flask, request, render_template, redirect, url_for, session
from models import db, User, Request, Feedback
import os

print("DB LOCATION: ", os.getcwd())

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "mysupersecretveryverydifficultkey"
db.init_app(app)

# with app.app_context():
#     db.create_all()

@app.route("/")
def home():
    return "SkillSwap running"

@app.route("/add_user")
def add_user():
    new_user = User(
        name="Test",
        email="test@test.com",
        password="123",
        skills_offered="python",
        skills_requested="design"
    )

    db.session.add(new_user)
    db.session.commit()

    return "User Added"

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        new_user = User(
            name = request.form['name'],
            email = request.form['email'],
            password = request.form['password'],
            skills_offered = request.form['skills_offered'],
            skills_requested = request.form['skills_requested'],
        )

        db.session.add(new_user)
        db.session.commit()

        return "Registered successfully"
    
    return render_template("register.html")

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password"
        
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return f"""
    <h2>Hello, {user.name}!</h2>
    <p><a href='/matches'>View Matches</a></p>
    <p><a href='/profile'>My Profile</a></p>
    <p><a href='/logout'>Logout</a></p>
    """

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/matches")
def matches():
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    matched_users = []
    users = User.query.all()

    for u in users:
        if u.id == current_user.id:
            continue
        # basic match logic: user wants what you offer AND offers what you want
        if current_user.skills_requested in u.skills_offered and \
           u.skills_requested in current_user.skills_offered:
            matched_users.append(u)

    return render_template("matches.html", users=matched_users)

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        user.name = request.form["name"]
        user.skills_offered = request.form["skills_offered"]
        user.skills_requested = request.form["skills_requested"]

        db.session.commit()
        return "Profile updated!"

    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)