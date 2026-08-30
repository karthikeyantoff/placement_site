from flask import Blueprint, request, jsonify, render_template, session
from bson import ObjectId
from models.database import get_db
from services.auth_service import login_required, roles_required
from services.cloudinary_service import upload_file

student_bp = Blueprint("student_api", __name__)
student_views_bp = Blueprint("student_views", __name__)

@student_bp.route("/test_cloudinary", methods=["GET"])
def test_cloudinary_endpoint():
    import io, base64
    import cloudinary, cloudinary.uploader
    from config import Config
    try:
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
            secure=True
        )
        png_bytes = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
        bio = io.BytesIO(png_bytes)
        bio.name = 'test.png'
        res = cloudinary.uploader.upload(bio, folder='student_photos', resource_type='auto')
        return jsonify({"success": True, "url": res.get("secure_url")})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()})

# Views
@student_views_bp.route("/admin/students", methods=["GET"])
@login_required
@roles_required("admin")
def admin_students_page():
    return render_template("admin/students.html")

@student_views_bp.route("/manager/students", methods=["GET"])
@login_required
@roles_required("manager")
def manager_students_page():
    return render_template("manager/students.html")

@student_views_bp.route("/student/<reg_number>", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def view_student_page(reg_number):
    role = session.get("role").lower()
    return render_template(f"{role}/student_view.html", reg_number=reg_number)


# API Endpoints
@student_bp.route("", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_students():
    db = get_db()
    query = {}
    
    # Live Search by Registration Number or Name
    search = request.args.get("search", "").strip()
    if search:
        query["$or"] = [
            {"reg_number": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}}
        ]
        
    students_cursor = db.students.find(query)
    students_list = []
    
    for s in students_cursor:
        s["_id"] = str(s["_id"])
        students_list.append(s)
        
    return jsonify(students_list)

@student_bp.route("/<reg_number>", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_student_by_reg(reg_number):
    db = get_db()
    import re
    student = db.students.find_one({"reg_number": {"$regex": f"^{re.escape(reg_number)}$", "$options": "i"}})
    if not student:
        return jsonify({"error": f"Student with registration number '{reg_number}' not found."}), 404
        
    student["_id"] = str(student["_id"])
    return jsonify(student)

@student_bp.route("", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def create_student():
    db = get_db()
    
    # Extract multipart text fields
    reg_number = request.form.get("reg_number", "").strip()
    name = request.form.get("name", "").strip()
    
    if not reg_number or not name:
        return jsonify({"error": "Registration Number and Student Name are required."}), 400
        
    # Check uniqueness
    if db.students.find_one({"reg_number": reg_number}):
        return jsonify({"error": f"Student with registration number '{reg_number}' already exists."}), 409
        
    # Handle file uploads to Cloudinary
    photo_file = request.files.get("photo")
    resume_file = request.files.get("resume")
    self_intro_file = request.files.get("self_intro")
    
    photo_url = upload_file(photo_file, folder="student_photos") if photo_file else ""
    resume_url = upload_file(resume_file, folder="student_resumes") if resume_file else ""
    self_intro_url = upload_file(self_intro_file, folder="student_self_intro") if self_intro_file else ""
    
    # Base Document
    student_doc = {
        "reg_number": reg_number,
        "name": name,
        "department": request.form.get("department", "").strip(),
        "gender": request.form.get("gender", "").strip(),
        "student_type": request.form.get("student_type", "").strip(), # Hosteller / Day Scholar
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        
        "sslc_percentage": float(request.form.get("sslc_percentage", 0) or 0),
        "hsc_percentage": float(request.form.get("hsc_percentage", 0) or 0),
        "ug_percentage": float(request.form.get("ug_percentage", 0) or 0),
        "pg_percentage": float(request.form.get("pg_percentage", 0)) if request.form.get("pg_percentage") else None,
        
        "github_link": request.form.get("github_link", "").strip(),
        "linkedin_link": request.form.get("linkedin_link", "").strip(),
        "resume_url": resume_url or request.form.get("resume_url", "").strip(),
        "self_intro_link": self_intro_url or request.form.get("self_intro_link", "").strip(),
        "photo_url": photo_url or request.form.get("photo_url", "").strip() or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
        "portfolio_link": request.form.get("portfolio_link", "").strip(),
        "year_of_graduation": int(request.form.get("year_of_graduation", 2025) or 2025),
        
        "placement_status": request.form.get("placement_status", "YTPP").strip(),
        "placed_company": request.form.get("placed_company", "").strip(),
        "ctc_lpa": float(request.form.get("ctc_lpa", 0)) if request.form.get("ctc_lpa") else None
    }
    
    result = db.students.insert_one(student_doc)
    student_doc["_id"] = str(result.inserted_id)
    
    # Audit log
    db.activity_logs.insert_one({
        "username": session.get("username"),
        "role": session.get("role"),
        "action": "Student Added",
        "target_type": "Student",
        "target_id": student_doc["_id"],
        "timestamp": "ISODate"
    })
    
    # Also sync placement record if PLACED
    if student_doc["placement_status"] == "PLACED" and student_doc["placed_company"]:
        db.placements.insert_one({
            "reg_number": student_doc["reg_number"],
            "student_name": student_doc["name"],
            "department": student_doc["department"],
            "company_name": student_doc["placed_company"],
            "status": "PLACED",
            "ctc_lpa": student_doc["ctc_lpa"] or 0.0,
            "drive_date": "",
            "offer_date": ""
        })
        
    return jsonify(student_doc), 201

@student_bp.route("/<student_id>", methods=["PUT"])
@login_required
@roles_required("admin", "manager")
def update_student(student_id):
    db = get_db()
    
    try:
        query = {"_id": ObjectId(student_id)}
    except Exception:
        query = {"reg_number": student_id}
        
    student = db.students.find_one(query)
    if not student:
        return jsonify({"error": "Student not found."}), 404
        
    # Handle file uploads
    photo_file = request.files.get("photo")
    resume_file = request.files.get("resume")
    self_intro_file = request.files.get("self_intro")
    
    photo_url = upload_file(photo_file, folder="student_photos") if photo_file else None
    resume_url = upload_file(resume_file, folder="student_resumes") if resume_file else None
    self_intro_url = upload_file(self_intro_file, folder="student_self_intro") if self_intro_file else None
    
    # Check if reg_number changed and if it is unique
    new_reg = request.form.get("reg_number", "").strip()
    if new_reg and new_reg != student["reg_number"]:
        if db.students.find_one({"reg_number": new_reg}):
            return jsonify({"error": f"Registration number '{new_reg}' is already taken."}), 409
            
    # Assemble updates
    updates = {}
    text_fields = [
        "name", "reg_number", "department", "gender", "student_type",
        "phone", "email", "github_link", "linkedin_link", "portfolio_link",
        "placement_status", "placed_company"
    ]
    
    for f in text_fields:
        val = request.form.get(f)
        if val is not None:
            updates[f] = val.strip()
            
    # Number fields
    if request.form.get("sslc_percentage") is not None:
        updates["sslc_percentage"] = float(request.form.get("sslc_percentage") or 0)
    if request.form.get("hsc_percentage") is not None:
        updates["hsc_percentage"] = float(request.form.get("hsc_percentage") or 0)
    if request.form.get("ug_percentage") is not None:
        updates["ug_percentage"] = float(request.form.get("ug_percentage") or 0)
    if request.form.get("pg_percentage") is not None:
        val = request.form.get("pg_percentage")
        updates["pg_percentage"] = float(val) if val.strip() else None
    if request.form.get("year_of_graduation") is not None:
        updates["year_of_graduation"] = int(request.form.get("year_of_graduation") or 2025)
    if request.form.get("ctc_lpa") is not None:
        val = request.form.get("ctc_lpa")
        updates["ctc_lpa"] = float(val) if val.strip() else None
        
    # File fields
    if photo_url:
        updates["photo_url"] = photo_url
    if resume_url:
        updates["resume_url"] = resume_url
    if self_intro_url:
        updates["self_intro_url"] = self_intro_url
        
    db.students.update_one({"_id": student["_id"]}, {"$set": updates})
    
    # Audit log
    db.activity_logs.insert_one({
        "username": session.get("username"),
        "role": session.get("role"),
        "action": "Student Edited",
        "target_type": "Student",
        "target_id": str(student["_id"]),
        "timestamp": "ISODate"
    })
    
    # Update Placements if status or company changes
    updated_student = db.students.find_one({"_id": student["_id"]})
    if updated_student.get("placement_status") == "PLACED":
        # Upsert placement
        db.placements.update_one(
            {"reg_number": updated_student["reg_number"]},
            {"$set": {
                "student_name": updated_student["name"],
                "department": updated_student["department"],
                "company_name": updated_student.get("placed_company", ""),
                "status": "PLACED",
                "ctc_lpa": updated_student.get("ctc_lpa") or 0.0
            }},
            upsert=True
        )
    else:
        # Remove from placed collection if it existed
        db.placements.delete_many({"reg_number": updated_student["reg_number"]})
        
    return jsonify({"success": True, "message": "Student updated successfully."})

@student_bp.route("/<student_id>", methods=["DELETE"])
@login_required
@roles_required("admin", "manager")
def delete_student(student_id):
    db = get_db()
    
    try:
        query = {"_id": ObjectId(student_id)}
    except Exception:
        query = {"reg_number": student_id}
        
    student = db.students.find_one(query)
    if not student:
        return jsonify({"error": "Student not found."}), 404
        
    # Delete from placements too
    db.placements.delete_many({"reg_number": student["reg_number"]})
    
    # Delete student
    db.students.delete_one({"_id": ObjectId(student_id)})
    
    # Audit log
    db.activity_logs.insert_one({
        "username": session.get("username"),
        "role": session.get("role"),
        "action": "Student Deleted",
        "target_type": "Student",
        "target_id": student_id,
        "timestamp": "ISODate"
    })
    
    return jsonify({"success": True, "message": "Student deleted successfully."})
