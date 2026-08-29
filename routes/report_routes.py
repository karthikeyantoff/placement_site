from flask import Blueprint, jsonify, request, render_template, session, Response
from bson import ObjectId
from models.database import get_db
from services.auth_service import login_required, roles_required
from services.pdf_service import generate_generic_report_pdf
import datetime

report_bp = Blueprint("report_api", __name__)
report_views_bp = Blueprint("report_views", __name__)

# Views
@report_views_bp.route("/admin/reports", methods=["GET"])
@login_required
@roles_required("admin")
def admin_reports_page():
    return render_template("admin/reports.html")

@report_views_bp.route("/manager/reports", methods=["GET"])
@login_required
@roles_required("manager")
def manager_reports_page():
    return render_template("manager/reports.html")


# Helper function to fetch data dynamically for PDF generation or Mail forwarding
def fetch_report_data(report_type, company_name=None, search=None, status=None, approval=None):
    db = get_db()
    data = []
    meta = {}
    
    if report_type == "student_company":
        query = {"placed_company": company_name}
        if not company_name or company_name.lower() == "all":
            query = {"placement_status": "PLACED"}
        students_cursor = db.students.find(query, {"reg_number": 1, "name": 1, "department": 1, "email": 1, "phone": 1, "ctc_lpa": 1})
        data = list(students_cursor)
        meta["company_name"] = company_name or "All Companies"
        
    elif report_type == "student_placed":
        students_cursor = db.students.find(
            {"placement_status": "PLACED"},
            {"name": 1, "reg_number": 1, "department": 1, "placed_company": 1, "ctc_lpa": 1}
        )
        data = list(students_cursor)
        
    elif report_type == "student_overall":
        students_cursor = db.students.find(
            {},
            {"name": 1, "reg_number": 1, "department": 1, "placed_company": 1, "ctc_lpa": 1, "placement_status": 1}
        )
        data = list(students_cursor)
        
    elif report_type == "company_pipeline":
        query = {}
        if search:
            query["company_name"] = {"$regex": search, "$options": "i"}
        if status:
            query["placement_status"] = status.upper()
        if approval:
            query["approval_status"] = approval.upper()
            
        companies_cursor = db.companies.find(query)
        data = list(companies_cursor)
        
    elif report_type == "company_drive":
        company = db.companies.find_one({"company_name": company_name})
        if company:
            placed_students = db.students.find(
                {"placed_company": company_name, "placement_status": "PLACED"},
                {"name": 1, "reg_number": 1, "department": 1, "phone": 1}
            )
            data = list(placed_students)
        meta["company_name"] = company_name or "Completed Drive"
        
    return data, meta


# API Endpoints

# 1. Student Report 1 - Company-wise registered/placed students
@report_bp.route("/students/company/<company_name>", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_company_registered_students(company_name):
    data, _ = fetch_report_data("student_company", company_name=company_name)
    for s in data:
        s["_id"] = str(s["_id"])
    return jsonify(data)

# 2. Student Report 2 - Drive completed status
@report_bp.route("/students/placed", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_drive_completed_placed():
    data, _ = fetch_report_data("student_placed")
    for s in data:
        s["_id"] = str(s["_id"])
    return jsonify(data)

# 3. Student Report 3 - Overall student placement info
@report_bp.route("/students/overall", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_overall_placement_info():
    data, _ = fetch_report_data("student_overall")
    for s in data:
        s["_id"] = str(s["_id"])
    return jsonify(data)

# 4. Company Report 1 - Company details & status tracker
@report_bp.route("/companies/status", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_companies_by_status():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    approval = request.args.get("approval", "").strip()
    
    data, _ = fetch_report_data("company_pipeline", search=search, status=status, approval=approval)
    for c in data:
        c["_id"] = str(c["_id"])
    return jsonify(data)

# 5. Company Report 2 - Drive completed companies & selections
@report_bp.route("/companies/completed", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def get_drive_completed_companies():
    db = get_db()
    companies_cursor = db.companies.find({
        "approval_status": "APPROVED",
        "placement_status": "DRIVE_COMPLETED"
    })
    
    result_list = []
    for c in companies_cursor:
        placed_students = db.students.find(
            {"placed_company": c["company_name"], "placement_status": "PLACED"},
            {"name": 1, "reg_number": 1, "department": 1, "phone": 1}
        )
        student_records = []
        for s in placed_students:
            s["_id"] = str(s["_id"])
            student_records.append(s)
            
        c["_id"] = str(c["_id"])
        c["selections"] = student_records
        if not c.get("offers_count") or c["offers_count"] == 0:
            c["offers_count"] = len(student_records)
        result_list.append(c)
        
    return jsonify(result_list)


# Dynamic PDF Exporter Route
@report_bp.route("/download-pdf", methods=["GET"])
@login_required
@roles_required("admin", "manager")
def download_generic_report_pdf():
    report_type = request.args.get("type", "").strip()
    company_name = request.args.get("company_name", "").strip()
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    approval = request.args.get("approval", "").strip()
    
    if not report_type:
        return jsonify({"error": "Report type is required."}), 400
        
    data, meta = fetch_report_data(report_type, company_name=company_name, search=search, status=status, approval=approval)
    
    if len(data) == 0:
        return jsonify({"error": "No records found matching query filter parameters to export."}), 404
        
    pdf_bytes = generate_generic_report_pdf(report_type, data, meta)
    
    filename = f"report_{report_type}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# Dynamic Mail/Proposal Forwarding Route
@report_bp.route("/forward-proposal", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def forward_generic_report_proposal():
    db = get_db()
    username = session.get("username")
    role = session.get("role")
    
    data_json = request.get_json() or {}
    report_type = data_json.get("type", "").strip()
    company_name = data_json.get("company_name", "").strip()
    search = data_json.get("search", "").strip()
    status = data_json.get("status", "").strip()
    approval = data_json.get("approval", "").strip()
    message_content = data_json.get("message", "").strip()
    
    if not report_type:
        return jsonify({"error": "Report type is required."}), 400
    if not message_content:
        return jsonify({"error": "Message content is required."}), 400
        
    records, meta = fetch_report_data(report_type, company_name=company_name, search=search, status=status, approval=approval)
    
    if len(records) == 0:
        return jsonify({"error": "No records found matching query filters to forward."}), 404
        
    # Format details into text list for mail content
    summary_lines = []
    if "student" in report_type:
        summary_lines = [f"- {item.get('name')} ({item.get('reg_number')}) [{item.get('department')}] - Status: {item.get('placement_status','PLACED')}" for item in records]
    else:
        summary_lines = [f"- {item.get('company_name')} [{item.get('location')}] - Pipeline: {item.get('placement_status')}" for item in records]
        
    full_message = f"{message_content}\n\nFiltered Records Summary:\n" + "\n".join(summary_lines)
    
    receiver = "sivasubramaniyan" if role.lower() == "manager" else "all"
    
    db.notifications.insert_one({
        "sender": username,
        "receiver": receiver,
        "type": "ANALYTICS_REPORT_PROPOSAL",
        "title": f"Report Forwarded: {report_type.replace('_',' ').title()}",
        "message": full_message,
        "status": "UNREAD",
        "created_at": datetime.datetime.utcnow().isoformat()
    })
    
    return jsonify({"success": True, "message": "Report proposal forwarded successfully!"})
