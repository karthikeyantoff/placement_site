import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "placement_mgmt_super_secret_key_2026"
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get("MONGO_URI") or "mongodb+srv://karthikeyantoff_db_user:mZ8U46NCo8J4skQR@cluster0.jzjhled.mongodb.net/placement_management?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = os.environ.get("DB_NAME") or "placement_management"
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME") or "cblqllb4"
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY") or "622793567484623"
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET") or "7PhnWLaCyqhoh0WbG29_zgEjhvw"
    
    # Uploads Fallback Folder
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
