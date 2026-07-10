from datetime import datetime,UTC
from extensions import db,login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

class User(db.Model,UserMixin):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),nullable=False)
    approved=db.Column(db.Boolean,default=False,nullable=False)
    blacklisted=db.Column(db.Boolean,default=False,nullable=False)
    created_at=db.Column(db.DateTime,default=lambda: datetime.now(UTC),nullable=False) #Lambda function is used here as a callable, so that we dont end up calling the function at server creation

    def set_password(self,password):
        self.password=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password,password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))



