import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

# Try importing cloudinary SDK
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

# Configure Cloudinary if credentials are provided
if CLOUDINARY_AVAILABLE and Config.CLOUDINARY_CLOUD_NAME and Config.CLOUDINARY_API_KEY and Config.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True
    )
    CLOUDINARY_CONFIGURED = True
else:
    CLOUDINARY_CONFIGURED = False

def upload_file(file_storage, folder="placement_system"):
    """
    Uploads a file to Cloudinary.
    If Cloudinary is not configured, it saves it locally under static/uploads/
    and returns a local URL path.
    """
    if not file_storage or file_storage.filename == "":
        return None

    filename = secure_filename(file_storage.filename)
    
    if CLOUDINARY_CONFIGURED:
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_storage,
                folder=folder,
                resource_type="auto"
            )
            return result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload failed: {e}. Falling back to local upload...")
            
    # Local Fallback
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    local_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file_storage.save(local_path)
    return f"/static/uploads/{unique_filename}"
