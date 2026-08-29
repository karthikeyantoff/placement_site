from functools import wraps
from flask import session, jsonify, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    if not password or not hashed_password:
        return False
    return check_password_hash(hashed_password, password)

def get_current_user():
    username = session.get("username")
    if not username:
        return None
    db = get_db()
    user = db.users.find_one({"username": username, "active": True}, {"password_hash": 0})
    if user and "_id" in user:
        user["_id"] = str(user["_id"])
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username") or not session.get("role"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Please log in.", "code": 401}), 401
            return redirect(url_for("auth_views.login_page"))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get("role")
            if not user_role:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Unauthorized. Please log in.", "code": 401}), 401
                return redirect(url_for("auth_views.login_page"))
            
            # Normalize roles
            allowed = [r.lower() for r in allowed_roles]
            if user_role.lower() not in allowed:
                if request.path.startswith("/api/"):
                    return jsonify({
                        "error": f"Forbidden. Role '{user_role}' does not have permission for this resource.",
                        "code": 403,
                        "required_roles": allowed_roles
                    }), 403
                return render_unauthorized_page(user_role, allowed_roles)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def render_unauthorized_page(current_role, required_roles):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>403 Forbidden - Access Denied</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white min-h-screen flex items-center justify-center p-4">
        <div class="bg-slate-800 border border-red-500/30 rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
            <div class="w-16 h-16 bg-red-500/20 text-red-400 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">403</div>
            <h1 class="text-2xl font-bold mb-2">Access Denied</h1>
            <p class="text-slate-400 mb-6">Your current role (<span class="text-amber-400 font-semibold uppercase">{current_role}</span>) does not have permission to access this page.</p>
            <a href="/dashboard" class="inline-block bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-2.5 rounded-xl transition">Return to Dashboard</a>
        </div>
    </body>
    </html>
    """, 403
