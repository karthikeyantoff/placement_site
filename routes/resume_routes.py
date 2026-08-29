from flask import Blueprint, request, jsonify, session, Response
from models.database import get_db
from services.auth_service import login_required, roles_required
from services.resume_matcher import match_resume_and_jd, extract_text_from_pdf, extract_text_from_url
from services.pdf_service import generate_resume_match_pdf
import datetime
import re
from bson import ObjectId

resume_bp = Blueprint("resume_api", __name__)

@resume_bp.route("/score", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def calculate_resume_score():
    db = get_db()
    is_json = request.is_json
    
    jd_title = ""
    reg_number = ""
    jd_text = ""
    jd_url = ""
    resume_url = ""
    
    if is_json:
        data = request.get_json() or {}
        jd_title = data.get("jd_title", "Custom Job Description").strip()
        reg_number = data.get("reg_number", "").strip()
        jd_text = data.get("jd_text", "").strip()
        jd_url = data.get("jd_url", "").strip()
        resume_url = data.get("resume_url", "").strip()
    else:
        jd_title = request.form.get("jd_title", "Custom Job Description").strip()
        reg_number = request.form.get("reg_number", "").strip()
        jd_text = request.form.get("jd_text", "").strip()
        jd_url = request.form.get("jd_url", "").strip()
        resume_url = request.form.get("resume_url", "").strip()
        
    jd_file = request.files.get("jd_file")
    resume_file = request.files.get("resume_file")
    
    # 1. Parse JD Text
    if jd_file and jd_file.filename != "":
        if jd_file.filename.lower().endswith(".pdf"):
            jd_text = extract_text_from_pdf(jd_file)
        else:
            jd_text = jd_file.read().decode("utf-8", errors="ignore")
    elif jd_url:
        jd_text = extract_text_from_url(jd_url)
            
    # 2. Parse Custom Resume Text
    custom_resume_text = None
    if resume_file and resume_file.filename != "":
        if resume_file.filename.lower().endswith(".pdf"):
            custom_resume_text = extract_text_from_pdf(resume_file)
    elif resume_url:
        custom_resume_text = extract_text_from_url(resume_url)
            
    if not jd_text:
        return jsonify({"error": "Job Description text, file, or link is required."}), 400
        
    student = None
    if reg_number:
        student = db.students.find_one({"reg_number": {"$regex": f"^{re.escape(reg_number)}$", "$options": "i"}})
        if not student and not custom_resume_text:
            return jsonify({"error": f"Student with registration number '{reg_number}' not found."}), 404
            
    if not student:
        student = {
            "name": request.form.get("custom_name", "Anonymous Candidate").strip(),
            "reg_number": reg_number or "TEMP_" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "department": "Custom Profile",
            "ug_percentage": 75.0
        }
        
    score, score_range, matched, missing = match_resume_and_jd(jd_text, student, custom_resume_text)
    
    score_doc = {
        "student_id": student.get("_id", ObjectId()),
        "reg_number": student["reg_number"],
        "student_name": student["name"],
        "department": student["department"],
        "jd_title": jd_title,
        "jd_text": jd_text[:2000],
        "score": score,
        "score_range": score_range,
        "matched_skills": matched,
        "missing_skills": missing,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    db.resume_scores.update_one(
        {"reg_number": student["reg_number"], "jd_title": jd_title},
        {"$set": score_doc},
        upsert=True
    )
    
    return jsonify({
        "success": True,
        "score": score,
        "score_range": score_range,
        "matched_skills": matched,
        "missing_skills": missing,
        "student_name": student["name"],
        "reg_number": student["reg_number"]
    })

@resume_bp.route("/bulk-score", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def calculate_bulk_scores():
    db = get_db()
    is_json = request.is_json
    
    jd_title = ""
    jd_text = ""
    jd_url = ""
    department = "ALL"
    
    if is_json:
        data = request.get_json() or {}
        jd_title = data.get("jd_title", "Bulk Match Job Description").strip()
        jd_text = data.get("jd_text", "").strip()
        jd_url = data.get("jd_url", "").strip()
        department = data.get("department", "ALL").strip().upper()
    else:
        jd_title = request.form.get("jd_title", "Bulk Match Job Description").strip()
        jd_text = request.form.get("jd_text", "").strip()
        jd_url = request.form.get("jd_url", "").strip()
        department = request.form.get("department", "ALL").strip().upper()
        
    jd_file = request.files.get("jd_file")
    
    # 1. Parse JD Text
    if jd_file and jd_file.filename != "":
        if jd_file.filename.lower().endswith(".pdf"):
            jd_text = extract_text_from_pdf(jd_file)
        else:
            jd_text = jd_file.read().decode("utf-8", errors="ignore")
    elif jd_url:
        jd_text = extract_text_from_url(jd_url)
        
    if not jd_text:
        return jsonify({"error": "Job Description text, file, or link is required."}), 400
        
    # 2. Query target students based on department choice
    query = {}
    if department != "ALL":
        query["department"] = {"$regex": f"^{re.escape(department)}$", "$options": "i"}
        
    students_cursor = db.students.find(query)
    students = list(students_cursor)
    
    if len(students) == 0:
        return jsonify({"error": f"No student records found in department '{department}'."}), 404
        
    # 3. Calculate matching score for all matching candidates
    results = []
    distribution = {
        "91-100": 0,
        "81-90": 0,
        "71-80": 0,
        "61-70": 0,
        "51-60": 0,
        "0-50": 0
    }
    
    for s in students:
        score, score_range, matched, missing = match_resume_and_jd(jd_text, s)
        
        score_doc = {
            "student_id": s["_id"],
            "reg_number": s["reg_number"],
            "student_name": s["name"],
            "department": s["department"],
            "jd_title": jd_title,
            "jd_text": jd_text[:2000],
            "score": score,
            "score_range": score_range,
            "matched_skills": matched,
            "missing_skills": missing,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        db.resume_scores.update_one(
            {"reg_number": s["reg_number"], "jd_title": jd_title},
            {"$set": score_doc},
            upsert=True
        )
        
        distribution[score_range] += 1
        results.append({
            "student_name": s["name"],
            "reg_number": s["reg_number"],
            "jd_title": jd_title,
            "score": score,
            "score_range": score_range
        })
        
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return jsonify({
        "success": True,
        "total_scanned": len(students),
        "distribution": distribution,
        "scores": results
    })

@resume_bp.route("/scores", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_resume_scores():
    db = get_db()
    
    pipeline = [
        {"$group": {
            "_id": "$score_range",
            "count": {"$sum": 1}
        }}
    ]
    
    distribution = {
        "91-100": 0,
        "81-90": 0,
        "71-80": 0,
        "61-70": 0,
        "51-60": 0,
        "0-50": 0
    }
    
    try:
        agg_result = db.resume_scores.aggregate(pipeline)
        for item in agg_result:
            rng = item["_id"]
            if rng in distribution:
                distribution[rng] = item["count"]
    except Exception:
        pass
        
    filter_range = request.args.get("range", "").strip()
    query = {}
    if filter_range:
        query["score_range"] = filter_range
        
    scores_cursor = db.resume_scores.find(query).sort("score", -1)
    scores_list = []
    
    for s in scores_cursor:
        s["_id"] = str(s["_id"])
        s["student_id"] = str(s["student_id"])
        scores_list.append(s)
        
    return jsonify({
        "distribution": distribution,
        "scores": scores_list
    })

@resume_bp.route("/download-pdf", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def download_resume_match_pdf_report():
    db = get_db()
    jd_title = request.args.get("jd_title", "").strip()
    if not jd_title:
        return jsonify({"error": "Job Description Title is required to download reports."}), 400
        
    scores_cursor = db.resume_scores.find({"jd_title": jd_title}).sort("score", -1)
    scores = list(scores_cursor)
    
    if len(scores) == 0:
        return jsonify({"error": f"No matches found for JD: '{jd_title}'."}), 404
        
    pdf_bytes = generate_resume_match_pdf(jd_title, scores)
    
    clean_title = "".join([c if c.isalnum() else "_" for c in jd_title])
    filename = f"match_report_{clean_title}.pdf"
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@resume_bp.route("/forward-proposal", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def forward_match_proposal():
    db = get_db()
    username = session.get("username")
    role = session.get("role")
    
    data = request.get_json() or {}
    jd_title = data.get("jd_title", "").strip()
    message_content = data.get("message", "").strip()
    
    if not jd_title:
        return jsonify({"error": "Job Description Title is required."}), 400
    if not message_content:
        return jsonify({"error": "Proposal mail content is required."}), 400
        
    scores_cursor = db.resume_scores.find({"jd_title": jd_title}).sort("score", -1)
    scores = list(scores_cursor)
    
    if len(scores) == 0:
        return jsonify({"error": f"No candidate scores found to forward for JD: '{jd_title}'."}), 404
        
    candidate_summary = "\n".join([f"- {s['student_name']} ({s['reg_number']}) - {s['score']}% Match" for s in scores])
    full_message = f"{message_content}\n\nCandidate Matching List:\n{candidate_summary}"
    
    # If sent by Manager, receiver is Admin (sivasubramaniyan)
    receiver = "sivasubramaniyan" if role.lower() == "manager" else "all"
    
    db.notifications.insert_one({
        "sender": username,
        "receiver": receiver,
        "type": "RESUME_MATCH_PROPOSAL",
        "title": f"Resume Match Mail: {jd_title}",
        "message": full_message,
        "status": "UNREAD",
        "created_at": datetime.datetime.utcnow().isoformat()
    })
    
    return jsonify({"success": True, "message": "Resume compatibility proposal forwarded successfully!"})
