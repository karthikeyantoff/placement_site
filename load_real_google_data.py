import csv
import os
import re
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/placement_management")
DB_NAME = os.environ.get("DB_NAME", "placement_management")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def clean_percent(val):
    if not val:
        return 0.0
    val_clean = val.replace("%", "").strip()
    try:
        return float(val_clean)
    except:
        return 0.0

def clean_ctc(val):
    if not val:
        return 0.0
    match = re.search(r"[\d\.]+", val)
    if match:
        try:
            return float(match.group(0))
        except:
            return 0.0
    return 0.0

def wipe_and_seed_real_data():
    print("Clearing all existing collections from Live MongoDB Atlas...")
    db.students.delete_many({})
    db.companies.delete_many({})
    db.placements.delete_many({})
    db.resume_scores.delete_many({})
    db.notifications.delete_many({})
    print("Old data completely wiped!")

    # 1. Parse Real Students
    students_to_insert = []
    student_file = os.path.join("datasets", "real_students.csv")
    
    with open(student_file, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        lines = list(reader)
        # Find header index
        header_idx = -1
        for idx, line in enumerate(lines):
            if line and "Roll No" in line[0]:
                header_idx = idx
                break
        
        if header_idx != -1:
            headers = lines[header_idx]
            for row in lines[header_idx+1:]:
                if not row or len(row) < 3 or not row[0].strip():
                    continue
                
                reg = row[0].strip()
                name = row[1].strip() if len(row) > 1 else ""
                dept = row[2].strip() if len(row) > 2 else ""
                gender = row[3].strip() if len(row) > 3 else "Male"
                student_type = row[4].strip() if len(row) > 4 else ""
                sslc = clean_percent(row[5]) if len(row) > 5 else 0.0
                hsc = clean_percent(row[6]) if len(row) > 6 else 0.0
                ug = clean_percent(row[7]) if len(row) > 7 else 0.0
                pg = clean_percent(row[8]) if len(row) > 8 else 0.0
                github = row[9].strip() if len(row) > 9 else ""
                resume_link = row[10].strip() if len(row) > 10 else ""
                linkedin = row[11].strip() if len(row) > 11 else ""
                portfolio = row[13].strip() if len(row) > 13 else ""
                p_email = row[14].strip() if len(row) > 14 else ""
                c_email = row[15].strip() if len(row) > 15 else ""
                phone = row[16].strip() if len(row) > 16 else ""
                photo_link = row[17].strip() if len(row) > 17 else ""
                status_raw = row[18].strip().upper() if len(row) > 18 else "YET_TO_BE_PLACED"
                
                status = "PLACED" if "PLACED" in status_raw and "YET" not in status_raw else "YET_TO_BE_PLACED"
                
                # Check placed company mapping
                placed_comp = ""
                ctc = 0.0
                if status == "PLACED":
                    placed_comp = "Zoho Corporation"
                    ctc = 8.5

                # Distinct high-res photo pools based on Gender
                male_photos = [
                    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=400&q=80"
                ]
                female_photos = [
                    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=400&q=80",
                    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80"
                ]
                
                if "female" in gender.lower():
                    final_photo = female_photos[idx % len(female_photos)]
                else:
                    final_photo = male_photos[idx % len(male_photos)]
                
                doc = {
                    "reg_number": reg,
                    "name": name,
                    "department": dept,
                    "gender": gender,
                    "student_type": student_type,
                    "email": c_email or p_email or f"{reg.lower()}@rathinam.in",
                    "personal_email": p_email,
                    "phone": phone or "9876543210",
                    "sslc_percentage": sslc,
                    "hsc_percentage": hsc,
                    "ug_percentage": ug,
                    "pg_percentage": pg,
                    "github_url": github,
                    "linkedin_url": linkedin,
                    "portfolio_url": portfolio,
                    "resume_url": resume_link,
                    "photo_url": final_photo,
                    "placement_status": status,
                    "placed_company": placed_comp if status == "PLACED" else "",
                    "ctc_lpa": ctc if status == "PLACED" else 0.0,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                students_to_insert.append(doc)
                
    if students_to_insert:
        db.students.insert_many(students_to_insert)
        print(f"Inserted {len(students_to_insert)} Real Students into Live MongoDB Atlas!")

    # 2. Parse Real Companies
    companies_to_insert = []
    company_file = os.path.join("datasets", "real_companies.csv")
    
    with open(company_file, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        lines = list(reader)
        header_idx = -1
        for idx, line in enumerate(lines):
            if line and "S.No" in line[0]:
                header_idx = idx
                break
                
        if header_idx != -1:
            for row in lines[header_idx+1:]:
                if not row or len(row) < 3 or not row[0].strip() or "Overall" in row[0]:
                    continue
                    
                c_name = row[1].strip()
                role = row[2].strip()
                ctc = clean_ctc(row[3])
                loc = row[4].strip()
                opp_status = row[5].strip() # DRIVE_COMPLETED, WARM, etc.
                app_status = row[6].strip() # APPROVED, PENDING_APPROVAL
                placed_cnt = int(row[7].strip()) if row[7].strip().isdigit() else 0
                placed_details = row[8].strip()
                jd_summary = row[9].strip()
                jd_pdf = row[10].strip()
                careers_link = row[11].strip()
                hr_email = row[12].strip()
                hr_phone = row[13].strip()
                
                # Normalize statuses
                norm_app = "APPROVED" if "APPROV" in app_status.upper() else "PENDING"
                norm_pipe = "DRIVE_COMPLETED" if "COMPLET" in opp_status.upper() else "HOT" if "HOT" in opp_status.upper() else "WARM"
                
                doc = {
                    "company_name": c_name,
                    "job_role": role,
                    "package_ctc": f"{ctc} LPA",
                    "ctc_lpa": ctc,
                    "location": loc,
                    "hr_email": hr_email or "hr@company.com",
                    "hr_phone": hr_phone or "+91 9876543210",
                    "sourcing_lead": "lead-1",
                    "placement_status": norm_pipe,
                    "approval_status": norm_app,
                    "offers_count": placed_cnt,
                    "placed_details": placed_details,
                    "jd_summary": jd_summary,
                    "jd_url": jd_pdf,
                    "careers_link": careers_link,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                companies_to_insert.append(doc)
                
                # Also update students who placed in this company!
                if placed_details and "(" in placed_details:
                    # Match name/reg from details e.g. "Adithya Venkatesh (RCAS2024BCS011)"
                    matches = re.findall(r"\(([A-Z0-9]+)\)", placed_details)
                    for reg_found in matches:
                        db.students.update_one(
                            {"reg_number": reg_found},
                            {"$set": {"placement_status": "PLACED", "placed_company": c_name, "ctc_lpa": ctc}}
                        )
                        # Add placement record
                        student_match = db.students.find_one({"reg_number": reg_found})
                        s_name = student_match["name"] if student_match else reg_found
                        s_dept = student_match["department"] if student_match else "CS"
                        db.placements.insert_one({
                            "reg_number": reg_found,
                            "student_name": s_name,
                            "department": s_dept,
                            "company_name": c_name,
                            "package_ctc": f"{ctc} LPA",
                            "ctc_lpa": ctc,
                            "offer_letter_url": f"https://example.com/offers/{reg_found}_offer.pdf",
                            "placed_date": datetime.datetime.utcnow().strftime("%Y-%m-%d")
                        })
                        
    if companies_to_insert:
        db.companies.insert_many(companies_to_insert)
        print(f"Inserted {len(companies_to_insert)} Real Companies into Live MongoDB Atlas!")

    # Initial Welcome System Notification
    db.notifications.insert_one({
        "sender": "System",
        "receiver": "sivasubramaniyan",
        "type": "SYSTEM_ALERT",
        "title": "Real Google Datasets Loaded",
        "message": f"Successfully loaded {len(students_to_insert)} unique student profiles and {len(companies_to_insert)} corporate recruitment drives from official Google Sheets.",
        "status": "UNREAD",
        "created_at": datetime.datetime.utcnow().isoformat()
    })
    
    print("\n--- Live Data Migration Complete ---")
    print(f"Students count in DB: {db.students.count_documents({})}")
    print(f"Companies count in DB: {db.companies.count_documents({})}")
    print(f"Placements count in DB: {db.placements.count_documents({})}")

if __name__ == "__main__":
    wipe_and_seed_real_data()
