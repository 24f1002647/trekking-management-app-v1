from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from models.user import User
from extensions import db

profile = Blueprint("profile", __name__)


@profile.route("/", methods=["GET", "POST"])
@login_required
def display_profile():

    if request.method == "POST":
        if current_user.role=="admin":
            flash("Admin cannot change credentials","danger")
            return redirect(url_for("profile.display_profile"))
        
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("profile.display_profile"))

        email = request.form.get("email", "").strip()
        if not email:
            flash("Email cannot be empty.", "danger")
            return redirect(url_for("profile.display_profile"))

        password = request.form.get("password", "").strip()
        if password:
            current_user.password = generate_password_hash(password)
        
        existing_user = User.query.filter(User.email == email,User.id != current_user.id).first()
        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for("profile.display_profile"))
        
        current_user.name = name
        current_user.email = email
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Something went wrong.", "danger")
            return redirect(url_for("profile.display_profile"))

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.display_profile"))

    return render_template("profile.html")