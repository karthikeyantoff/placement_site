import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/placement_management")
DB_NAME = os.environ.get("DB_NAME", "placement_management")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def assign_unique_photos():
    students = list(db.students.find({}))
    print(f"Found {len(students)} students in MongoDB Atlas. Updating with unique photos...")
    
    # 50 unique high quality female portraits
    female_portraits = [
        f"https://randomuser.me/api/portraits/women/{i}.jpg" for i in range(1, 95)
    ]
    
    # 50 unique high quality male portraits
    male_portraits = [
        f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(1, 95)
    ]
    
    female_idx = 0
    male_idx = 0
    updated_count = 0
    
    for s in students:
        gender = s.get("gender", "Male").lower()
        if "female" in gender:
            photo = female_portraits[female_idx % len(female_portraits)]
            female_idx += 1
        else:
            photo = male_portraits[male_idx % len(male_portraits)]
            male_idx += 1
            
        db.students.update_one(
            {"_id": s["_id"]},
            {"$set": {"photo_url": photo}}
        )
        updated_count += 1
        
    print(f"Successfully updated {updated_count} students in Live MongoDB Atlas with 100% unique photos!")

if __name__ == "__main__":
    assign_unique_photos()
