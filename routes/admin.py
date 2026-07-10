from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required
from utils.decorators import admin_required 
from models.user import User

from extensions import db

admin=Blueprint("admin",__name__)
@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users=User.query.filter_by(role="user").count()
    total_staff=User.query.filter_by(role="staff").count()
    pending_staff=User.query.filter_by(role="staff",approved=False).count()
    return render_template("admin/dashboard.html",total_users=total_users,total_staff=total_staff,pending_staff=pending_staff)

@admin.route('/staff')
@login_required
@admin_required
def display_staff():
    staff_members=User.query.filter_by(role="staff").all()
    return render_template("admin/staff.html",staff_members=staff_members)

@admin.route("/staff/<int:id>/approve",methods=["POST"])
@login_required
@admin_required
def approve_staff(id):
    staff=get_staff(id)
    if not staff:
        flash("The staff member does not exist","danger")
        return redirect(url_for("admin.display_staff"))
    if staff.blacklisted:
        flash("The member is blacklisted. Cannot Approve","danger")
        return redirect(url_for("admin.display_staff"))
    if staff.approved:
        flash("Member already approved","warning")
        return redirect(url_for("admin.display_staff"))
    staff.approved=True

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong","danger")
        return redirect(url_for("admin.display_staff"))
    flash("Staff member approved","success")
    return redirect(url_for("admin.display_staff"))
    
#Helper function to get the staff if exising, else None
def get_staff(id):
    return User.query.filter_by(id=id,role="staff").first()


@admin.route("/staff/<int:id>/blacklist",methods=["POST"])
@login_required
@admin_required
def blacklist(id):
    staff=get_staff(id)
    if not staff:
        flash("Staff does not exist","danger")
        return redirect(url_for("admin.display_staff"))

    if staff.blacklisted:
        flash("Staff already blacklisted","danger")
        return redirect(url_for("admin.display_staff"))
    staff.blacklisted=True
    staff.approved=False

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong","danger")
        return redirect(url_for("admin.display_staff"))

    flash("Staff successfully blacklisted","success")
    return redirect(url_for("admin.display_staff"))

@admin.route("/staff/<int:id>/unblacklist",methods=["POST"])
@login_required
@admin_required
def unblacklist(id):
    staff=get_staff(id)
    if not staff:
        flash("Staff does not exist","danger")
        return redirect(url_for("admin.display_staff"))

    if not staff.blacklisted:
        flash("Staff is not blacklisted","warning")
        return redirect(url_for("admin.display_staff"))
    staff.blacklisted=False
    staff.approved=False

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong","danger")
        return redirect(url_for("admin.display_staff"))
    flash("Staff successfully unblacklisted","success")
    return redirect(url_for("admin.display_staff"))

        