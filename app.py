from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from middlewares.tokens import generate_token
from middlewares.decorator import jwt_required
import os
from dotenv import load_dotenv

load_dotenv() 

from models import ModuleRequest, User, Feedback, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

db.init_app(app)

with app.app_context():
    db.create_all()

# Decorator for HTML session routes
from functools import wraps
def session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# Public Routes
@app.route("/")
def home():
    return "SkillSwap running"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            skills_offered=request.form['skills_offered'],
            skills_requested=request.form['skills_requested'],
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"})
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # Handle JSON API login
    if request.is_json:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id)

    if request.is_json:
        return jsonify({"token": token})
    else:
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))

@app.route("/logout")
@session_required
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# HTML Session Protected Routes
@app.route("/dashboard")
@session_required
def dashboard():
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)

@app.route("/matches")
@session_required
def matches():
    current_user = User.query.get(session["user_id"])
    requested_skills = [s.strip().lower() for s in current_user.skills_requested.split(",") if s.strip()]
    offered_skills = [s.strip().lower() for s in current_user.skills_offered.split(",") if s.strip()]

    matched_users = []
    for u in User.query.all():
        if u.id == current_user.id:
            continue
        u_offered = [s.strip().lower() for s in u.skills_offered.split(",") if s.strip()]
        u_requested = [s.strip().lower() for s in u.skills_requested.split(",") if s.strip()]
        if any(skill in u_offered for skill in requested_skills) and any(skill in offered_skills for skill in u_requested):
            matched_users.append(u)
    return render_template("matches.html", users=matched_users)

@app.route("/profile", methods=["GET", "POST"])
@session_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        offered = request.form.get("skills_offered", user.skills_offered)
        requested = request.form.get("skills_requested", user.skills_requested)

        user.skills_offered = ", ".join([s.strip().lower() for s in offered.split(",") if s.strip()])
        user.skills_requested = ", ".join([s.strip().lower() for s in requested.split(",") if s.strip()])
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

@app.route("/request", methods=["GET", "POST"])
@session_required
def request_module():
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
@session_required
def all_modules():
    modules = ModuleRequest.query.all()
    return render_template("modules.html", modules=modules)

@app.route("/add_module/<int:module_id>")
@session_required
def add_module(module_id):
    module = ModuleRequest.query.get(module_id)
    user = User.query.get(session["user_id"])

    if module.requested_by == user.id:
        return "You cannot add your own requested module to your skills.", 403

    if module.title.lower() not in user.skills_offered.lower():
        user.skills_offered += f", {module.title}"

    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/contact/<int:target_user_id>", methods=["GET", "POST"])
@session_required
def contact(target_user_id):
    current_user_id = session["user_id"]
    target_user = User.query.get(target_user_id)
    if not target_user:
        return "User not found", 404

    if request.method == "POST":
        message = request.form["message"]
        new_feedback = Feedback(
            sender_id=current_user_id,
            receiver_id=target_user.id,
            message=message
        )
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for("contact", target_user_id=target_user_id))

    messages = Feedback.query.filter(
        ((Feedback.sender_id == current_user_id) & (Feedback.receiver_id == target_user_id)) |
        ((Feedback.sender_id == target_user_id) & (Feedback.receiver_id == current_user_id))
    ).order_by(Feedback.id.asc()).all()

    return render_template(
        "contact.html",
        user=target_user,
        messages=messages,
        current_user_id=current_user_id
    )

if __name__ == "__main__":
    app.run(debug=True)
