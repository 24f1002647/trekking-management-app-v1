from flask import Flask,render_template
from extensions import db,migrate,login_manager

from config import Config
from seed_admin import seed_admin

app=Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app,db)
login_manager.init_app(app)
login_manager.login_view="auth.login"
import models

from routes.auth import auth
from routes.admin import admin
from routes.staff import staff
from routes.user import user
app.register_blueprint(auth)
app.register_blueprint(admin,url_prefix="/admin")
app.register_blueprint(staff,url_prefix="/staff")
app.register_blueprint(user,url_prefix="/user")


@app.route("/")
def home():
    return render_template('index.html')

if __name__=="__main__":
    seed_admin(app)
    app.run(debug=True)
