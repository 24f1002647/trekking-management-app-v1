
from models.user import User
from extensions import db
ADMIN_EMAIL="admin123@example.com"
ADMIN_PASSWORD="admin123"
def seed_admin(app):
    with app.app_context():
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        if admin is None:
            admin = User(
                name="Admin",
                email=ADMIN_EMAIL,
                role="admin",
                approved=True,
                blacklisted=False
            )
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print("Admin created.")
        else:
            print("Admin already exists.")
