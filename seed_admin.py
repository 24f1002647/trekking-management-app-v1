
from models.user import User
from extensions import db
ADMIN_EMAIL="admin123@example.com"
ADMIN_PASSWORD="admin123"
def seed_admin(app):
    with app.app_context():
        admin=User.query.filter_by(email=ADMIN_EMAIL).first() #ensures that the admin is not preexisting, even if admin email has a typo
        if admin is None:
            admin=User(name="admin",email=ADMIN_EMAIL,role="admin",approved=True)
            admin.set_password(ADMIN_PASSWORD) 
            db.session.add(admin)
            db.session.commit()
        else:
            print("Admin already exists!!")
    
