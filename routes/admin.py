from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required
from utils.decorators import admin_required 

from models.user import User
from models.trek import Trek
from models.booking import Booking

from datetime import datetime

from extensions import db

admin=Blueprint("admin",__name__)
@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users=User.query.filter_by(role="user").count()
    total_staff=User.query.filter_by(role="staff").count()
    pending_staff=User.query.filter_by(role="staff",approved=False).count()

    total_treks=Trek.query.count()
    total_bookings=Booking.query.count()
    open_treks=Trek.query.filter_by(status="Open").count()
    completed_treks=Trek.query.filter_by(status="Completed").count()
    return render_template("admin/dashboard.html",total_users=total_users,total_staff=total_staff,
                           pending_staff=pending_staff,total_treks=total_treks,total_bookings=total_bookings,
                           open_treks=open_treks,completed_treks=completed_treks)

"""  Staff Module   """

@admin.route('/staff')
@login_required
@admin_required
def display_staff():
    search = request.args.get("search", "").strip()
    query = User.query.filter_by(role="staff")
    if search:
        if search.isdigit():
            query = query.filter(
                (User.id == int(search)) |
                (User.name.ilike(f"%{search}%"))
            )
        else:
            query = query.filter(User.name.ilike(f"%{search}%"))

    staff_members = query.all()
    return render_template("admin/staff.html",staff_members=staff_members,search=search)

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



@admin.route("/staff/<int:id>/blacklist",methods=["POST"])
@login_required
@admin_required
def blacklist_staff(id):
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
def unblacklist_staff(id):
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

""" User Module """
@admin.route('/users')
@login_required
@admin_required
def display_users():
    search=request.args.get("search","").strip()
    query=User.query.filter_by(role="user")

    if search:
        if search.isdigit():
            query = query.filter(
                (User.id == int(search)) |
                (User.name.ilike(f"%{search}%"))
            )
        else:
            query = query.filter(User.name.ilike(f"%{search}%"))
    user_members=query.all()

    return render_template("admin/user.html",user_members=user_members,search=search)

@admin.route("/users/<int:id>/blacklist",methods=["POST"])
@login_required
@admin_required
def blacklist_user(id):
    user=get_user(id)
    if not user:
        flash("User does not exist","danger")
        return redirect(url_for("admin.display_users"))

    if user.blacklisted:
        flash("User already blacklisted","danger")
        return redirect(url_for("admin.display_users"))
    user.blacklisted=True
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong","danger")
        return redirect(url_for("admin.display_users"))
    flash("User successfully blacklisted","success")
    return redirect(url_for("admin.display_users"))

@admin.route("/users/<int:id>/unblacklist",methods=["POST"])
@login_required
@admin_required
def unblacklist_user(id):
    user=get_user(id)

    if not user:
        flash("User does not exist","danger")
        return redirect(url_for("admin.display_users"))
    
    if not user.blacklisted:
        flash("User is not blacklisted","warning")
        return redirect(url_for("admin.display_users"))
    
    user.blacklisted=False
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong","danger")
        return redirect(url_for("admin.display_users"))
    flash("User successfully unblacklisted","success")
    return redirect(url_for("admin.display_users"))

""" Admin Trek Module """
@admin.route("/treks")
@login_required
@admin_required
def display_treks():

    search = request.args.get("search", "").strip()
    query = Trek.query
    if search:
        if search.isdigit():
            query = query.filter(
                (Trek.id == int(search)) |
                (Trek.name.ilike(f"%{search}%"))
            )
        else:
            query = query.filter(
                Trek.name.ilike(f"%{search}%")
            )
        
    treks = query.all()
    return render_template(
        "admin/treks.html",
        treks=treks,
        search=search
    )

@admin.route("/treks/create",methods=["GET","POST"])
@login_required
@admin_required
def create_trek():
    staff_members=User.query.filter_by(role="staff",approved=True,blacklisted=False).all()
    if request.method=="POST":
        name=request.form.get("name").strip()
        location=request.form.get("location").strip()
        description=request.form.get("description","").strip()
        difficulty=request.form.get("difficulty")
        
        duration=request.form.get("duration", type=int)
        capacity=request.form.get("capacity", type=int)
        if duration < 1 or capacity < 1:
            flash("Duration and capacity must be greater than zero.", "danger")
            return redirect(url_for("admin.create_trek"))

        start_date=datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
        end_date=datetime.strptime(request.form.get("end_date"),"%Y-%m-%d").date()
        if end_date<start_date:
            flash("End date cannot be before the start date","danger")
            return redirect(url_for("admin.create_trek"))
        
        staff_id=request.form.get("staff_id")
        if staff_id:
            staff_id=int(staff_id)
            staff=User.query.filter_by(id=staff_id,role="staff",approved=True,blacklisted=False).first()
            if not staff:
                flash("Invalid Staff","danger")
                return redirect(url_for("admin.create_trek"))
        else:
            staff_id=None
        trek = Trek(
        name=name,
        location=location,
        description=description,
        difficulty=difficulty,
        duration=duration,
        capacity=capacity,
        available_slots=capacity,
        start_date=start_date,
        end_date=end_date,
        staff_id=staff_id
        )
        db.session.add(trek)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Something went wrong.", "danger")
            return redirect(url_for("admin.create_trek"))
        flash("Trek created successfully.", "success")
        return redirect(url_for("admin.display_treks"))

    return render_template("admin/create_trek.html",staff_members=staff_members)

@admin.route("/treks/<int:id>/edit",methods=["GET","POST"])
@login_required
@admin_required
def edit_trek(id):
    trek=get_trek(id)
    if not trek:
        flash("Trek not found","danger")
        return redirect(url_for("admin.display_treks"))
    staff_members=User.query.filter_by(role="staff",approved=True,blacklisted=False).all()

    if request.method=="POST":
        if trek.status == "Completed":
            flash("Completed treks cannot be modified.","warning")
            return redirect(url_for("admin.display_treks"))
        
        name=request.form.get("name").strip()
        location=request.form.get("location").strip()
        description=request.form.get("description","").strip()
        difficulty=request.form.get("difficulty")
        status=request.form.get("status")
        duration=request.form.get("duration",type=int)
        capacity=request.form.get("capacity",type=int)
        start_date=datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
        end_date=datetime.strptime(request.form.get("end_date"),"%Y-%m-%d").date()

        if duration < 1 or capacity < 1:
            flash("Duration and capacity must be greater than zero.", "danger")
            return redirect(url_for("admin.edit_trek",id=trek.id))

        if end_date<start_date:
            flash("End date cannot be before the start date","danger")
            return redirect(url_for("admin.edit_trek",id=trek.id))
        
        staff_id=request.form.get("staff_id")
        if staff_id:
            staff_id=int(staff_id)
            staff=User.query.filter_by(id=staff_id,role="staff",approved=True,blacklisted=False).first()
            if not staff:
                flash("Invalid Staff","danger")
                return redirect(url_for("admin.edit_trek",id=trek.id))
        else:
            staff_id=None
        
        #booking validation
        booked_users=trek.capacity-trek.available_slots
        if capacity<booked_users:
            flash("Cannot reduce capacity below the number of booked users.","danger")
            return redirect(url_for("admin.edit_trek",id=trek.id))
        
        #status validation
        if status == "Completed":
            for booking in trek.bookings:
                if booking.status == "Booked":
                    booking.status = "Completed"


        #Updating the trek object
        trek.available_slots=capacity-booked_users
        trek.name = name
        trek.location = location
        trek.description = description
        trek.difficulty = difficulty

        trek.duration = duration
        trek.capacity = capacity

        trek.start_date = start_date
        trek.end_date = end_date

        trek.staff_id = staff_id
        trek.status = status
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Something went wrong.", "danger")
            return redirect(url_for("admin.edit_trek", id=trek.id))

        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.display_treks"))
    
    return render_template("admin/edit_trek.html",trek=trek,staff_members=staff_members)

@admin.route("/treks/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_trek(id):
    trek = get_trek(id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect(url_for("admin.display_treks"))
    if trek.bookings:
        flash(
            "Cannot delete a trek that has existing bookings.",
            "warning"
        )
        return redirect(url_for("admin.display_treks"))
    try:
        db.session.delete(trek)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong.", "danger")
        return redirect(url_for("admin.display_treks"))

    flash("Trek deleted successfully.", "success")
    return redirect(url_for("admin.display_treks"))

@admin.route("/bookings")
@login_required
@admin_required
def display_bookings():
    bookings=Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template("admin/bookings.html",bookings=bookings)




""" Helper Functions"""    
#Helper function to get the staff if exising, else None
def get_staff(id):
    return User.query.filter_by(id=id,role="staff").first()

#Helper function to get the user if exising, else None
def get_user(id):
    return User.query.filter_by(id=id,role="user").first()

def get_trek(id):
    return db.session.get(Trek,id)