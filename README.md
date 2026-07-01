[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/RlRKNPRa)

# GDPBZN Dispatch & Operations Platform

A web-based dispatch and operations management system for a fire and emergency response unit (ГДПБЗН — Главна дирекция "Пожарна безопасност и защита на населението"), built with Flask. It covers incident intake and tracking, crew and vehicle management, task assignment, shift scheduling, leave requests, and real-time in-incident chat with SOS alerting.

Built as a university practicum (praktika) project.

## Features

- **Incident management** — log incidents with type/priority/status, GPS location, hazard notes, and an action plan; assign a crew and vehicle; track the full timeline (reported → dispatched → on scene → resolved).
- **Task management** — create and edit tasks tied to an incident, assign them to a crew, and track status (pending / accepted / in progress / completed / cancelled).
- **Crew & vehicle management** — organize firefighters into crews, add/remove members, and track vehicle status (available / deployed / maintenance / retired).
- **Shift scheduling** — start and end shifts, pairing a crew with a vehicle.
- **Leave requests** — firefighters can request leave; ops/admin can approve or deny.
- **Real-time chat** — a per-incident chat channel (via Flask-SocketIO) for coordinating with a crew on scene, including image uploads.
- **SOS alerts** — a persistent SOS button for firefighters in the field, with an alert history and live acknowledgement flow for the operations center.
- **Live operations map** — real-time crew and vehicle positions via a JSON API, for dispatch/command visibility.
- **Mobile dashboard** — a lightweight, mobile-first view for firefighters showing their active assignments and tasks.
- **Role-based access control** — Admin, Operations Center, Dispatcher, and Firefighter roles, each with different permissions.
- **Admin panel** — manage user accounts and roles.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Flask-WTF, Flask-SocketIO
- **Database:** SQLite (dev), via SQLAlchemy ORM
- **Real-time:** Flask-SocketIO / python-socketio
- **Frontend:** Jinja2 templates, Bootstrap-based UI, vanilla JS (including a GPS tracker script for the mobile view)
- **Testing:** pytest, pytest-flask

## Project Structure

```
backend/
├── app/
│   ├── blueprints/        # Feature modules: auth, incidents, tasks, crews,
│   │                      #   vehicles, shifts, leave, operations, chat, admin
│   ├── models/             # SQLAlchemy models (User, Crew, Vehicle, Incident,
│   │                       #   Task, Message, SOSAlert, LeaveRequest, ...)
│   ├── static/              # CSS, JS (incl. gps_tracker.js), uploaded chat images
│   ├── templates/           # Jinja2 templates, organized per blueprint
│   ├── utils/                # Role-based decorators, message templates
│   └── socket_events.py       # SocketIO event handlers
├── migrations/                # Alembic database migrations
├── tests/                     # pytest test suite
├── config.py                  # App configuration (dev/prod)
├── run.py                      # Application entry point
└── seed.py                     # Wipes and repopulates the DB with demo data
```

## Getting Started

### Prerequisites

- Python 3.10+ (developed against 3.14)
- pip

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd praktika/backend

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file in backend/ (see "Environment Variables" below)

# 5. Set up the database
flask db upgrade
# — or, for a quick start with realistic sample data instead —
python seed.py
```

### Environment Variables

Create a `backend/.env` file with:

```
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=replace-this-with-a-real-secret-key
DATABASE_URL=sqlite:///gdpbzn.db
```

### Running the App

```bash
python run.py
```

The app runs at `http://localhost:5000`. **Note:** the app uses SocketIO for real-time chat and SOS alerts — always start it with `python run.py` (which calls `socketio.run()`), not `flask run`.

### Demo / Seed Data

`seed.py` drops and recreates all tables, then populates the database with a full showcase dataset — sample users, crews, vehicles, incidents at every stage, tasks, chat messages, and an active SOS alert.

```bash
cd backend
python seed.py
```

⚠️ **This deletes all existing data.** Only run it in development, or intentionally before a demo.

Demo accounts created by the seed script (password shown per role):

| Username      | Password    | Role               |
|---------------|-------------|--------------------|
| `admin`       | `admin1234` | Admin              |
| `ops1`        | `ops11234`  | Operations Center  |
| `dispatcher1` | `disp1234`  | Dispatcher         |
| `ff1`–`ff7`   | `fire1234`  | Firefighter        |

These are development-only credentials — change or remove them before any real deployment.

### Running Tests

```bash
cd backend
pytest
```

## Contributors

- Kaloyan Boychev
- V. A. Tenev

## License

No license has been specified for this project. All rights reserved by the authors unless stated otherwise.

