from flask import Flask, request, render_template, redirect, url_for, session
from models import ModuleRequest, db, User, Feedback
import os

print("DB LOCATION: ", os.getcwd())

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "mysupersecretveryverydifficultkey"
db.init_app(app)

with app.app_context():
    db.create_all()

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
    return render_template("dashboard.html", user=user)

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
        offered = request.form["skills_offered"]
        requested = request.form["skills_requested"]

        user.skills_offered = ", ".join(
            [s.strip().lower() for s in offered.split(",") if s.strip()]
        )

        user.skills_requested = ", ".join(
            [a.strip().lower() for a in requested.split(",") if a.strip()]
        )

        db.session.commit()
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route("/request", methods=["GET","POST"])
def request_module():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        module = ModuleRequest(
            title=request.form["title"],
            description=request.form["description"],
            requested_by=session["user_id"]
        )
        db.session.add(module)
        db.session.commit()
        return redirect(url_for("all_modules"))
    
    return render_template("request.html")

@app.route("/modules")
def all_modules():
    modules = ModuleRequest.query.all()
    return render_template("modules.html", modules=modules)

@app.route("/add_module/<int:module_id>")
def add_module(module_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    module = ModuleRequest.query.get(module_id)
    user = User.query.get(session["user_id"])

    if module.title.lower() not in user.skills_offered.lower():
        user.skills_offered += f", {module.title}"

    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/contact/<int:user_id>", methods=["GET", "POST"])
def contact(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user_id = session["user_id"]
    target_user = User.query.get(user_id)

    if not target_user:
        return "User not found", 404

    if request.method == "POST":
        new_feedback = Feedback(
            sender_id=current_user_id,
            receiver_id=target_user.id,
            message=request.form["message"]
        )
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for("contact", user_id=user_id))

    messages = Feedback.query.filter(
        ((Feedback.sender_id == current_user_id) & (Feedback.receiver_id == user_id)) |
        ((Feedback.sender_id == user_id) & (Feedback.receiver_id == current_user_id))
    ).order_by(Feedback.id.asc()).all()

    return render_template(
        "contact.html",
        user=target_user,
        messages=messages,
        current_user_id=current_user_id
    )



if __name__ == "__main__":
    app.run(debug=True)