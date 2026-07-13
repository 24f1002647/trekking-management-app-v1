from flask import Blueprint,render_template,flash,redirect,url_for,request
from flask_login import login_required,current_user

from extensions import db

from models.trek import Trek
from models.booking import Booking

from utils.decorators import staff_required


staff=Blueprint("staff",__name__)

@staff.route("/dashboard")
@login_required
@staff_required
def dashboard():
    assigned_treks=Trek.query.filter_by(staff_id=current_user.id).all()
    return render_template("staff/dashboard.html",assigned_treks=assigned_treks)

@staff.route("/treks/<int:id>",methods=["GET","POST"])
@login_required
@staff_required
def manage_trek(id):    
    trek=db.session.get(Trek,id)
    if not trek:
        flash("Trek not found","danger")
        return redirect(url_for("staff.dashboard"))
    if trek.staff_id != current_user.id:
        flash("You are not assigned this trek.","danger")
        return redirect(url_for("staff.dashboard"))
    bookings=Booking.query.filter_by(trek_id=trek.id).all()

    if request.method=="POST":
        if trek.status == "Completed":
            flash("Completed treks cannot be modified.", "warning")
            return redirect(url_for("staff.manage_trek", id=trek.id))
        
        status=request.form.get("status")
        available_slots=request.form.get("available_slots",type=int)
        
        if available_slots<0:
            flash("Available slots cannot be negative","danger")
            return redirect(url_for("staff.manage_trek",id=trek.id))
        
        booked_users=trek.capacity-trek.available_slots

        if available_slots < trek.available_slots:
            flash("Staff cannot reduce available slots.","danger")
            return redirect(url_for("staff.manage_trek", id=trek.id))
        
        
        trek.status=status
        if status=="Completed":
            for booking in bookings:
                if booking.status=="Booked":
                    booking.status="Completed"

        trek.available_slots=available_slots
        trek.capacity=booked_users+available_slots
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Something went wrong.", "danger")
            return redirect(url_for("staff.manage_trek", id=trek.id))
        
        flash("Trek updated successfully.", "success")
        return redirect(url_for("staff.manage_trek", id=trek.id))
    
    return render_template("staff/manage_trek.html",trek=trek,bookings=bookings)