from functools import wraps
from flask import session
from models import User, db

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if user_id is None:
            return {
                "error": "Authentication required."
            },401

        return fn(*args, **kwargs)

    return wrapper

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")

            if user_id is None:
                return {
                    "error": "Authentication required."
                }, 401

            user = db.session.get(User, user_id)

            if user is None:
                session.clear()
                return {
                    "error": "Invalid session."
                }, 401

            print("Session role:", session.get("role"))
            print("User role:", user.role.value)
            print("Allowed roles:", roles)

            if user.role.value not in roles:
                return {
                    "error": "Forbidden."
                }, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator