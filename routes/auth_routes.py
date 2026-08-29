from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from models.database import get_db
from services.auth_service import verify_password, get_current_user

auth_bp = Blueprint("auth", __name__)
auth_views_bp = Blueprint("auth_views", __name__)

@auth_views_bp.route("/", methods=["GET"])
def index():
    if session.get("username") and session.get("role"):
        return redirect(url_for("auth_views.dashboard_page"))
    return redirect(url_for("auth_views.login_page"))

@auth_views_bp.route("/login", methods=["GET"])
def login_page():
    if session.get("username") and session.get("role"):
        return redirect(url_for("auth_views.dashboard_page"))
    return render_template("login.html")

@auth_views_bp.route("/dashboard", methods=["GET"])
def dashboard_page():
    role = session.get("role")
    username = session.get("username")
    name = session.get("name", "User")
    
    if not role or not username:
        return redirect(url_for("auth_views.login_page"))
        
    role_lower = role.lower()
    if role_lower == "admin":
        return render_template("admin/dashboard.html", username=username, role=role, name=name)
    elif role_lower == "manager":
        return render_template("manager/dashboard.html", username=username, role=role, name=name)
    elif role_lower == "lead":
        return render_template("lead/dashboard.html", username=username, role=role, name=name)
    else:
        session.clear()
        return redirect(url_for("auth_views.login_page"))

@auth_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    selected_role = data.get("role", "").strip().lower() # admin, manager, lead
    
    if not username or not password or not selected_role:
        return jsonify({"error": "Username, password and role selection are required."}), 400
        
    db = get_db()
    user = db.users.find_one({"username": username, "active": True})
    
    if not user:
        return jsonify({"error": "Invalid username or account is disabled."}), 401
        
    # Check if the user's role matches the selected login role
    if user.get("role", "").lower() != selected_role:
        return jsonify({"error": f"Role mismatch. User '{username}' is not registered as a {selected_role}."}), 401
        
    # Verify password hash
    if not verify_password(password, user.get("password_hash")):
        return jsonify({"error": "Incorrect password."}), 401
        
    # Set session details
    session.clear()
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["name"] = user.get("name", user["username"])
    
    # Store user login activity log
    try:
        db.activity_logs.insert_one({
            "username": user["username"],
            "role": user["role"],
            "action": "Login",
            "target_type": "User",
            "target_id": str(user["_id"]),
            "timestamp": "ISODate"
        })
    except Exception:
        pass
        
    return jsonify({
        "success": True,
        "message": f"Welcome back, {session['name']}!",
        "user": {
            "username": session["username"],
            "role": session["role"],
            "name": session["name"]
        },
        "redirect_url": url_for("auth_views.dashboard_page")
    })

@auth_bp.route("/logout", methods=["POST"])
def api_logout():
    username = session.get("username")
    role = session.get("role")
    
    if username:
        try:
            db = get_db()
            db.activity_logs.insert_one({
                "username": username,
                "role": role,
                "action": "Logout",
                "target_type": "User",
                "target_id": "",
                "timestamp": "ISODate"
            })
        except Exception:
            pass
            
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
        "redirect_url": url_for("auth_views.login_page")
    })

@auth_bp.route("/me", methods=["GET"])
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({
        "authenticated": True,
        "user": user
    })
