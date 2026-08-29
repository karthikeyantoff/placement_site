from flask import Blueprint, jsonify, session, render_template
from bson import ObjectId
from models.database import get_db
from services.auth_service import login_required

notification_bp = Blueprint("notification_api", __name__)
notification_views_bp = Blueprint("notification_views", __name__)

# Views
@notification_views_bp.route("/admin/mail", methods=["GET"])
@login_required
def admin_mail_page():
    return render_template("admin/mail.html")

@notification_views_bp.route("/lead/mail", methods=["GET"])
@login_required
def lead_mail_page():
    return render_template("lead/mail.html")

# API
@notification_bp.route("", methods=["GET"])
@login_required
def get_notifications():
    db = get_db()
    username = session.get("username")
    
    # Fetch notifications where the current user is the receiver
    notifications_cursor = db.notifications.find({"receiver": username}).sort("created_at", -1)
    notifications_list = []
    
    for n in notifications_cursor:
        n["_id"] = str(n["_id"])
        if "company_id" in n and n["company_id"]:
            n["company_id"] = str(n["company_id"])
        notifications_list.append(n)
        
    return jsonify(notifications_list)

@notification_bp.route("/<notification_id>/read", methods=["PUT"])
@login_required
def mark_as_read(notification_id):
    db = get_db()
    username = session.get("username")
    
    result = db.notifications.update_one(
        {"_id": ObjectId(notification_id), "receiver": username},
        {"$set": {"status": "READ"}}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "Notification not found or unauthorized access."}), 404
        
    return jsonify({"success": True, "message": "Notification marked as read."})
