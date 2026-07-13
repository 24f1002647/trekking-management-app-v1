from flask import Blueprint,render_template,flash,redirect,url_for,request
from flask_login import login_required,current_user
from models.trek import Trek
from models.booking import Booking
from extensions import db
from utils.decorators import user_required

user=Blueprint("user",__name__)

@user.route("/dashboard")
@login_required
@user_required
def dashboard():
    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()

    query = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0
    )
    if search:
        query = query.filter(Trek.name.ilike(f"%{search}%"))

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    available_treks = query.all()

    active_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).count()

    completed_treks = Booking.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).count()
    return render_template(
        "user/dashboard.html",
        available_treks=available_treks,
        search=search,
        difficulty=difficulty,
        location=location,
        active_bookings=active_bookings,
        completed_treks=completed_treks
    )

@user.route("/treks/<int:id>/book",methods=["POST"])
@login_required
@user_required
def book_trek(id):
    trek=db.session.get(Trek,id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect(url_for("user.dashboard"))
    if current_user.blacklisted:
        flash("You are blacklisted and cannot book treks.", "danger")
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
@user_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template(
        "user/bookings.html",
        bookings=bookings
    )

@user.route("/bookings/<int:id>/cancel",methods=["POST"])
@login_required
@user_required
def cancel_booking(id):
    if current_user.blacklisted:
        flash("You are blacklisted.", "danger")
        return redirect(url_for("user.my_bookings"))
    
    booking=db.session.get(Booking,id)

    if not booking:
        flash("Booking not found","danger")
        return redirect(url_for("user.my_bookings"))
    if booking.user_id!=current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("user.my_bookings"))
    if booking.trek.status == "Completed":
        flash("Completed treks cannot be cancelled.", "warning")
        return redirect(url_for("user.my_bookings"))
    if booking.status != "Booked":
        flash("This booking cannot be cancelled.", "danger")
        return redirect(url_for("user.my_bookings"))
    
    booking.status = "Cancelled"
    booking.trek.available_slots += 1

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("Something went wrong.", "danger")
        return redirect(url_for("user.my_bookings"))
    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("user.my_bookings"))
