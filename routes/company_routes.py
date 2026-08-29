from flask import Blueprint, request, jsonify, render_template, session, Response
from bson import ObjectId
from models.database import get_db
from services.auth_service import login_required, roles_required
from services.pdf_service import generate_company_pdf
import datetime

company_bp = Blueprint("company_api", __name__)
company_views_bp = Blueprint("company_views", __name__)

# Views
@company_views_bp.route("/admin/companies", methods=["GET"])
@login_required
@roles_required("admin")
def admin_companies_page():
    return render_template("admin/companies.html")

@company_views_bp.route("/lead/placement", methods=["GET"])
@login_required
@roles_required("lead")
def lead_placement_page():
    return render_template("lead/placement.html")

# API Endpoints
@company_bp.route("", methods=["GET"])
@login_required
@roles_required("admin", "lead")
def get_companies():
    db = get_db()
    role = session.get("role").lower()
    username = session.get("username")
    
    query = {}
    # Lead can only see their own submitted/drafted companies
    if role == "lead":
        query["submitted_by"] = username
        
    search = request.args.get("search", "").strip()
    if search:
        query["$or"] = [
            {"company_name": {"$regex": search, "$options": "i"}},
            {"location": {"$regex": search, "$options": "i"}}
        ]
        
    companies_cursor = db.companies.find(query)
    companies_list = []
    
    for c in companies_cursor:
        c["_id"] = str(c["_id"])
        companies_list.append(c)
        
    return jsonify(companies_list)

@company_bp.route("/<company_id>", methods=["GET"])
@login_required
@roles_required("admin", "lead")
def get_company(company_id):
    db = get_db()
    role = session.get("role").lower()
    username = session.get("username")
    
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    # Security: Leads can only view their own companies
    if role == "lead" and company.get("submitted_by") != username:
        return jsonify({"error": "Forbidden. You do not have access to this company."}), 403
        
    company["_id"] = str(company["_id"])
    return jsonify(company)

@company_bp.route("", methods=["POST"])
@login_required
@roles_required("admin", "lead")
def create_company():
    db = get_db()
    data = request.get_json() or {}
    
    company_name = data.get("company_name", "").strip()
    if not company_name:
        return jsonify({"error": "Company Name is required."}), 400
        
    # Check if company already exists
    if db.companies.find_one({"company_name": company_name}):
        return jsonify({"error": f"Company '{company_name}' already exists."}), 409
        
    username = session.get("username")
    role = session.get("role").lower()
    
    # Save Draft
    company_doc = {
        "company_name": company_name,
        "location": data.get("location", "").strip(),
        "website": data.get("website", "").strip(),
        "content": data.get("content", "").strip(),
        "hr_phone": data.get("hr_phone", "").strip(),
        "hr_email": data.get("hr_email", "").strip(),
        "company_address": data.get("company_address", "").strip(),
        
        "approval_status": "PENDING",
        "placement_status": "COLD",
        "submitted_by": username,
        "approved_by": "",
        "drive_date": data.get("drive_date") or None,
        "offers_count": int(data.get("offers_count") or 0),
        "is_forwarded": False,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    result = db.companies.insert_one(company_doc)
    company_doc["_id"] = str(result.inserted_id)
    
    # Audit log
    db.activity_logs.insert_one({
        "username": username,
        "role": session.get("role"),
        "action": "Company Added",
        "target_type": "Company",
        "target_id": company_doc["_id"],
        "timestamp": "ISODate"
    })
    
    return jsonify(company_doc), 201

@company_bp.route("/<company_id>", methods=["PUT"])
@login_required
@roles_required("admin", "lead")
def update_company(company_id):
    db = get_db()
    role = session.get("role").lower()
    username = session.get("username")
    
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    # Security: Leads can only edit their own drafts
    if role == "lead":
        if company.get("submitted_by") != username:
            return jsonify({"error": "Forbidden. You can only update your own sourced companies."}), 403
        if company.get("approval_status") == "APPROVED":
            return jsonify({"error": "Forbidden. Approved companies cannot be edited by Leads."}), 403
            
    data = request.get_json() or {}
    updates = {}
    
    # Fields editable by both Lead and Admin
    fields = ["location", "website", "content", "hr_phone", "hr_email", "company_address"]
    for f in fields:
        if f in data:
            updates[f] = data[f].strip()
            
    # Admin can edit status parameters, drive date, and offers
    if role == "admin":
        if "approval_status" in data:
            updates["approval_status"] = data["approval_status"]
        if "placement_status" in data:
            updates["placement_status"] = data["placement_status"]
        if "drive_date" in data:
            updates["drive_date"] = data["drive_date"]
        if "offers_count" in data:
            updates["offers_count"] = int(data["offers_count"] or 0)
            
    updates["updated_at"] = datetime.datetime.utcnow().isoformat()
    db.companies.update_one({"_id": ObjectId(company_id)}, {"$set": updates})
    
    # Audit log
    db.activity_logs.insert_one({
        "username": username,
        "role": session.get("role"),
        "action": "Company Edited",
        "target_type": "Company",
        "target_id": company_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Company details updated successfully."})

@company_bp.route("/<company_id>", methods=["DELETE"])
@login_required
@roles_required("admin")
def delete_company(company_id):
    db = get_db()
    
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    db.companies.delete_one({"_id": ObjectId(company_id)})
    
    # Audit log
    db.activity_logs.insert_one({
        "username": session.get("username"),
        "role": "admin",
        "action": "Company Deleted",
        "target_type": "Company",
        "target_id": company_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Company deleted successfully."})

@company_bp.route("/<company_id>/forward", methods=["POST"])
@login_required
@roles_required("lead")
def forward_company(company_id):
    db = get_db()
    username = session.get("username")
    
    company = db.companies.find_one({"_id": ObjectId(company_id), "submitted_by": username})
    if not company:
        return jsonify({"error": "Company not found or unauthorized access."}), 404
        
    if company.get("is_forwarded"):
        return jsonify({"error": "Company has already been forwarded to Admin."}), 400
        
    db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"is_forwarded": True, "forwarded_at": datetime.datetime.utcnow().isoformat()}}
    )
    
    # Create notification for admin (Sivasubramaniyan)
    db.notifications.insert_one({
        "sender": username,
        "receiver": "sivasubramaniyan",
        "type": "COMPANY_SUBMISSION",
        "company_id": ObjectId(company_id),
        "company_name": company["company_name"],
        "title": f"New Company Sourced: {company['company_name']}",
        "message": f"{username} has submitted {company['company_name']} for admin background verification.",
        "status": "UNREAD",
        "created_at": datetime.datetime.utcnow().isoformat()
    })
    
    # Audit log
    db.activity_logs.insert_one({
        "username": username,
        "role": "lead",
        "action": "Company Forwarded",
        "target_type": "Company",
        "target_id": company_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Company successfully forwarded to Admin for verification."})

@company_bp.route("/<company_id>/approve", methods=["POST"])
@login_required
@roles_required("admin")
def approve_company(company_id):
    db = get_db()
    admin_user = session.get("username")
    
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {
            "approval_status": "APPROVED",
            "approved_by": admin_user,
            "approved_at": datetime.datetime.utcnow().isoformat()
        }}
    )
    
    # Send notification alert to the Lead who submitted it
    lead_user = company.get("submitted_by")
    if lead_user:
        db.notifications.insert_one({
            "sender": admin_user,
            "receiver": lead_user,
            "type": "COMPANY_APPROVED",
            "company_id": ObjectId(company_id),
            "company_name": company["company_name"],
            "title": f"Company Approved: {company['company_name']}",
            "message": f"Company {company['company_name']} has been approved.\nNice job!\nKeep going and connect with the next company.",
            "status": "UNREAD",
            "created_at": datetime.datetime.utcnow().isoformat()
        })
        
    # Audit log
    db.activity_logs.insert_one({
        "username": admin_user,
        "role": "admin",
        "action": "Company Approved",
        "target_type": "Company",
        "target_id": company_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Company approved successfully."})

@company_bp.route("/<company_id>/reject", methods=["POST"])
@login_required
@roles_required("admin")
def reject_company(company_id):
    db = get_db()
    admin_user = session.get("username")
    
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {
            "approval_status": "REJECTED",
            "approved_by": admin_user,
            "approved_at": datetime.datetime.utcnow().isoformat()
        }}
    )
    
    # Send alert to Lead
    lead_user = company.get("submitted_by")
    if lead_user:
        db.notifications.insert_one({
            "sender": admin_user,
            "receiver": lead_user,
            "type": "COMPANY_REJECTED",
            "company_id": ObjectId(company_id),
            "company_name": company["company_name"],
            "title": f"Company Rejected: {company['company_name']}",
            "message": f"Company {company['company_name']} was rejected during background verification.",
            "status": "UNREAD",
            "created_at": datetime.datetime.utcnow().isoformat()
        })
        
    # Audit log
    db.activity_logs.insert_one({
        "username": admin_user,
        "role": "admin",
        "action": "Company Rejected",
        "target_type": "Company",
        "target_id": company_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Company verification rejected successfully."})

@company_bp.route("/<company_id>/pdf", methods=["GET"])
@login_required
@roles_required("admin")
def download_company_pdf(company_id):
    db = get_db()
    company = db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        return jsonify({"error": "Company not found."}), 404
        
    pdf_data = generate_company_pdf(company)
    
    # Generate cleaner filename
    clean_name = "".join([c if c.isalnum() else "_" for c in company["company_name"]])
    filename = f"company_{clean_name}.pdf"
    
    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
