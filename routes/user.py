from flask import Blueprint,render_template,flash,redirect,url_for
from flask_login import login_required,current_user
from models.trek import Trek
from models.booking import Booking
from extensions import db

user=Blueprint("user",__name__)

@user.route("/dashboard")
@login_required
def dashboard():
    available_treks=Trek.query.filter(Trek.status == "Open",Trek.available_slots > 0).all()
    return render_template("user/dashboard.html",available_treks=available_treks)

@user.route("/treks/<int:id>/book",methods=["POST"])
@login_required
def book_trek(id):
    trek=db.session.get(Trek,id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect(url_for("user.dashboard"))
    if current_user.blacklisted:
        flash("You are blacklisted and cannot book treks.", "danger")
        return redirect(url_for("user.dashboard"))
    if current_user.role != "user":
        flash("Only users can book treks.", "danger")
        return redirect(url_for("user.dashboard"))
    if trek.status != "Open":
        flash("This trek is not open for booking.","danger")
        return redirect(url_for("user.dashboard"))
    if trek.available_slots <= 0:
        flash("No slots available.", "warning")
        return redirect(url_for("user.dashboard"))   
     
    existing_booking=Booking.query.filter_by(user_id=current_user.id,trek_id=trek.id,status="Booked").first()
    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.dashboard"))
    booking=Booking(user_id=current_user.id,trek_id=trek.id)

    trek.available_slots-=1

    db.session.add(booking)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong.", "danger")
        return redirect(url_for("user.dashboard"))
    
    flash("Trek booked successfully!", "success")
    return redirect(url_for("user.dashboard"))

@user.route("/bookings")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    return render_template(
        "user/bookings.html",
        bookings=bookings
    )