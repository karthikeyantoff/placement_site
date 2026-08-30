import os
import shutil
import cloudinary
import cloudinary.uploader
from config import Config
from models.database import get_db

# Configure Cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True
)

source_img = r"C:\Users\Karthikeyan\.gemini\antigravity\brain\9699e12c-b9ec-44ea-bc60-61c83cf7d5e5\.user_uploaded\media_1788093323916.jpg"
reg_no = "RCAS2024BCS153"

print(f"Uploading photo for {reg_no} to Cloudinary...")

# Upload to Cloudinary
result = cloudinary.uploader.upload(
    source_img,
    folder="student_photos",
    public_id=f"student_{reg_no}",
    overwrite=True,
    resource_type="image"
)

cloudinary_url = result.get("secure_url")
print(f"Uploaded to Cloudinary: {cloudinary_url}")

# Save local copy
local_dir = r"d:\placement_site\static\images\students"
os.makedirs(local_dir, exist_ok=True)
local_dest = os.path.join(local_dir, f"{reg_no}.jpg")
shutil.copy(source_img, local_dest)
print(f"Saved local copy to {local_dest}")

# Update Live MongoDB Atlas
db = get_db()
res = db.students.update_one(
    {"reg_number": reg_no},
    {"$set": {"photo_url": cloudinary_url}}
)

print(f"MongoDB Atlas Update Result: matched={res.matched_count}, modified={res.modified_count}")
updated_student = db.students.find_one({"reg_number": reg_no})
print(f"Updated Student Profile: {updated_student['name']} ({updated_student['reg_number']}) -> photo_url: {updated_student['photo_url']}")
