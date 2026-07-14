import os

class Config:
    SECRET_KEY = "trekking-management-secret-key"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Create the database folder automatically if it doesn't exist
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    os.makedirs(DATABASE_DIR, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(DATABASE_DIR, "trekking.db")
    )
    # SQLALCHEMY_DATABASE_URI ="sqlite:///trekking.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False