from functools import wraps
from flask_login import current_user
from flask import redirect,url_for,flash
def admin_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.role=="admin":
            return func(*args,**kwargs)
        
        flash("You are not authorized to access this","danger")
        return redirect(url_for(f"{current_user.role}.dashboard"))
    return wrapper

def staff_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.role=="staff":
            return func(*args,**kwargs)
        
        flash("You are not authorized to access this","danger")
        return redirect(url_for(f"{current_user.role}.dashboard"))
    return wrapper

def user_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.role=="user":
            return func(*args,**kwargs)
        
        flash("You are not authorized to access this","danger")
        return redirect(url_for(f"{current_user.role}.dashboard"))
    return wrapper
