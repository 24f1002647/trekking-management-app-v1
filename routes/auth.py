from flask import Blueprint,request,render_template,flash,redirect,url_for
from flask_login import login_user,logout_user,login_required,current_user
from models.user import User

from extensions import db

auth=Blueprint("auth",__name__)
@auth.route('/login',methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}.dashboard"))
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        user=User.query.filter_by(email=email).first()

        if user is None:
            flash("Invalid email or password","danger")
            return redirect(url_for("auth.login"))

        if not user.check_password(password):
            flash("Invalid email or password","danger")
            return redirect(url_for("auth.login"))
        
        if not user.approved:
            flash("Your account is awaiting approval","warning")
            return redirect(url_for("auth.login"))
        if user.blacklisted:
            flash("Your account is blacklisted","danger")
            return redirect(url_for("auth.login"))
            
        print("User from DB:", user.email)
        print("Role from DB:", user.role)
        login_user(user)
        flash("Welcome Back","success")
        return redirect(url_for(f"{current_user.role}.dashboard"))

    return render_template("auth/login.html")

@auth.route('/register',methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}.dashboard"))
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        password=request.form.get("password")
        role=request.form.get("role")
        if not name:
            flash("Enter a valid name","danger")
            return redirect(url_for("auth.register"))
        if not email:
            flash("Enter a valid email","danger")
            return redirect(url_for("auth.register"))
        if not password:
            flash("Enter a password","danger")
            return redirect(url_for("auth.register"))
        if not role:
            flash("Select a role","danger")
            return redirect(url_for("auth.register"))
        
        if role not in ("user","staff"):
            flash("Select a valid role","danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first() is not None:
            flash("Email already exists","danger")
            return redirect(url_for("auth.register"))
        new_user=User(name=name,email=email,role=role,approved=(role=="user"))
        new_user.set_password(password)
        
        #implementing exception handling here, in case db transaction fails
        try:
            db.session.add(new_user)
            db.session.commit()
            if role=="user":
                flash("User created successfully","success")
            elif role=="staff":
                flash("Staff created successfully, awaiting admin approval","success")
        except Exception as e:
            print(e)#printing the exception in terminal, so that it is easier to debug
            db.session.rollback()
            flash("Sorry, we are having troubles right now. Please try again later.","danger")
            return redirect(url_for("auth.register"))
        return redirect(url_for("auth.login"))
     
    return render_template("auth/register.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully","success")
    return redirect(url_for("auth.login"))

