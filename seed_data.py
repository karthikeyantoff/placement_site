import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def seed_database(db=None):
    from services.auth_service import hash_password
    if db is None:
        from models.database import get_db
        db = get_db()
        
    datasets_dir = os.path.join(BASE_DIR, "datasets")
    
    # 1. Seed Users
    user_file = os.path.join(datasets_dir, "users.csv")
    if os.path.exists(user_file):
        with open(user_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            users_seeded = 0
            for row in reader:
                existing = db.users.find_one({"username": row["username"]})
                if not existing:
                    # Let's secure store the hashed password
                    hashed = hash_password(row["password_raw"])
                    db.users.insert_one({
                        "username": row["username"],
                        "name": row["name"],
                        "role": row["role"],
                        "email": row["email"],
                        "password_hash": hashed,
                        "active": row["active"] == "true"
                    })
                    users_seeded += 1
            if users_seeded > 0:
                print(f"Seeded {users_seeded} users into database.")
            else:
                print("Users collection already seeded.")
                
    # 2. Seed Students
    student_file = os.path.join(datasets_dir, "students.csv")
    if os.path.exists(student_file):
        with open(student_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            students_seeded = 0
            for row in reader:
                existing = db.students.find_one({"reg_number": row["reg_number"]})
                if not existing:
                    # Convert fields where appropriate
                    student_doc = {
                        "reg_number": row["reg_number"],
                        "name": row["name"],
                        "department": row["department"],
                        "gender": row["gender"],
                        "student_type": row["student_type"],
                        "phone": row["phone"],
                        "email": row["email"],
                        "sslc_percentage": float(row["sslc_percentage"]) if row["sslc_percentage"] else 0.0,
                        "hsc_percentage": float(row["hsc_percentage"]) if row["hsc_percentage"] else 0.0,
                        "ug_percentage": float(row["ug_percentage"]) if row["ug_percentage"] else 0.0,
                        "pg_percentage": float(row["pg_percentage"]) if row["pg_percentage"] else None,
                        "github_link": row["github_link"],
                        "linkedin_link": row["linkedin_link"],
                        "resume_url": row["resume_url"],
                        "self_intro_link": row["self_intro_link"],
                        "photo_url": row["photo_url"],
                        "portfolio_link": row["portfolio_link"],
                        "year_of_graduation": int(row["year_of_graduation"]) if row["year_of_graduation"] else 2025,
                        "placement_status": row["placement_status"],
                        "placed_company": row["placed_company"],
                        "ctc_lpa": float(row["ctc_lpa"]) if row["ctc_lpa"] else None
                    }
                    db.students.insert_one(student_doc)
                    students_seeded += 1
            if students_seeded > 0:
                print(f"Seeded {students_seeded} students into database.")
            else:
                print("Students collection already seeded.")
                
    # 3. Seed Companies
    company_file = os.path.join(datasets_dir, "companies.csv")
    if os.path.exists(company_file):
        with open(company_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            companies_seeded = 0
            for row in reader:
                existing = db.companies.find_one({"company_name": row["company_name"]})
                if not existing:
                    db.companies.insert_one({
                        "company_name": row["company_name"],
                        "location": row["location"],
                        "website": row["website"],
                        "content": row["content"],
                        "hr_phone": row["hr_phone"],
                        "hr_email": row["hr_email"],
                        "company_address": row["company_address"],
                        "approval_status": row["approval_status"],
                        "placement_status": row["placement_status"],
                        "submitted_by": row["submitted_by"],
                        "approved_by": row["approved_by"],
                        "drive_date": row["drive_date"] if row["drive_date"] else None,
                        "offers_count": int(row["offers_count"]) if row["offers_count"] else 0
                    })
                    companies_seeded += 1
            if companies_seeded > 0:
                print(f"Seeded {companies_seeded} companies into database.")
            else:
                print("Companies collection already seeded.")

    # 4. Seed Placements
    placement_file = os.path.join(datasets_dir, "placements.csv")
    if os.path.exists(placement_file):
        with open(placement_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            placements_seeded = 0
            for row in reader:
                existing = db.placements.find_one({
                    "reg_number": row["reg_number"],
                    "company_name": row["company_name"]
                })
                if not existing:
                    db.placements.insert_one({
                        "reg_number": row["reg_number"],
                        "student_name": row["student_name"],
                        "department": row["department"],
                        "company_name": row["company_name"],
                        "status": row["status"],
                        "ctc_lpa": float(row["ctc_lpa"]) if row["ctc_lpa"] else 0.0,
                        "drive_date": row["drive_date"],
                        "offer_date": row["offer_date"]
                    })
                    placements_seeded += 1
            if placements_seeded > 0:
                print(f"Seeded {placements_seeded} placements into database.")
            else:
                print("Placements collection already seeded.")

    # 5. Seed Notifications
    notification_file = os.path.join(datasets_dir, "notifications.csv")
    if os.path.exists(notification_file):
        with open(notification_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            notifications_seeded = 0
            for row in reader:
                existing = db.notifications.find_one({
                    "sender": row["sender"],
                    "receiver": row["receiver"],
                    "company_name": row["company_name"],
                    "type": row["type"]
                })
                if not existing:
                    db.notifications.insert_one({
                        "sender": row["sender"],
                        "receiver": row["receiver"],
                        "type": row["type"],
                        "company_name": row["company_name"],
                        "title": row["title"],
                        "message": row["message"],
                        "status": row["status"],
                        "created_at": row["created_at"]
                    })
                    notifications_seeded += 1
            if notifications_seeded > 0:
                print(f"Seeded {notifications_seeded} notifications into database.")
            else:
                print("Notifications collection already seeded.")

if __name__ == "__main__":
    seed_database()
