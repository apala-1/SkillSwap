# SkillSwap

SkillSwap is a Flask-based web application that allows users to exchange skills. Users can register, log in, request modules (skills), view matches based on skills offered and requested, and manage their profile.

## Features

- **User Registration & Login:** Secure registration and login with session management.
- **Profile Management:** Update personal information, skills offered, and skills requested.
- **Skill Requests:** Users can request new skills/modules.
- **Matches:** Automatic skill matching with other users based on requested and offered skills.
- **Module Management:** Users can add modules to their skills (excluding their own requests).
- **Contact/Feedback:** Users can message each other within the platform.

## Folder Structure

SKILLSWAP/
├── app.py # Main Flask application
├── models.py # Database models
├── instance/
│ └── database.db # SQLite database
├── static/
│ └── style.css # Optional CSS file
├── templates/ # HTML templates
│ ├── contact.html
│ ├── dashboard.html
│ ├── login.html
│ ├── matches.html
│ ├── modules.html
│ ├── profile.html
│ ├── register.html
│ └── request.html
└── venv/ # Python virtual environment


## Installation

1. Clone the repository:

```bash
git clone <repo_url>
cd SKILLSWAP
```
2. Create a virtual environment:
```bash
python -m venv venv
```
3. Activate the virtual environment:
-> Windows:
```bash
venv\Scripts\activate
```
-> Linux / macOS:
```bash
source venv/bin/activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
Note: Make sure Flask and SQLAlchemy are installed.
5. Run the app:
```bash
python app.py
```
6. Open your browser and navigate to http://127.0.0.1:5000.

# Usage

1. Register – Create a new user account with name, email, password, skills offered, and skills requested.
2. Login – Enter your email and password.
3. Dashboard – View your profile summary and navigate to modules, matches, or contact pages.
4. Profile – Update your information and skills.
5. Request Module – Submit a new skill/module request.
6. Modules – Browse requested modules and add other users’ skills to your profile (your own requests are disabled).
7. Matches – See users who match your requested skills and vice versa.
8. Contact – Message other users directly within the platform.

# Notes
1. Users cannot add their own requested modules to their skills.
2. Skill matching is case-insensitive and supports multiple comma-separated skills.
3. Database is SQLite (instance/database.db), created automatically on the first run.
