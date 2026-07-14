# Trekking Management Application

A role-based web application built using **Flask** for managing trekking activities.

## Features

- Role-based Authentication (Admin, Staff, User)
- Trek Management
- Trek Booking System
- Booking History
- Staff Approval & Management
- User & Staff Blacklisting
- Responsive Bootstrap UI
- Profile Management

---

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- SQLite
- Jinja2
- Bootstrap 5

---

## Installation

### 1. Clone the repository

### 2. Create a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
flask db upgrade
```

### 5. Run the application

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Default Admin Credentials

```
Email: admin123@example.com
Password: admin123
```

The admin account is created automatically on the first run if it does not already exist.

---

## Project Structure

```
models/         Database models
routes/         Flask Blueprints
templates/      Jinja2 templates
database/       SQLite database
migrations/     Flask-Migrate files
utils/          Helper functions & decorators
```

---

## Author

**Sambhav Shrivastava**
