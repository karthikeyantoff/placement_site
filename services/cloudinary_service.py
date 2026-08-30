import os
import uuid
import base64
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

def get_cloudinary_configured():
    if CLOUDINARY_AVAILABLE and Config.CLOUDINARY_CLOUD_NAME and Config.CLOUDINARY_API_KEY and Config.CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
            secure=True
        )
        return True
    return False

def upload_file(file_storage, folder="placement_system"):
    """
    Uploads a file to Cloudinary.
    If Cloudinary fails or is unavailable:
    - Attempts local disk storage (development)
    - Falls back to inline base64 Data URI on read-only serverless environments (Vercel)
    """
    if not file_storage or not getattr(file_storage, "filename", None):
        return None

    filename = secure_filename(file_storage.filename)
    
    # 1. Try Cloudinary Upload
    if get_cloudinary_configured():
        try:
            file_storage.seek(0)
            result = cloudinary.uploader.upload(
                file_storage,
                folder=folder,
                resource_type="auto"
            )
            if result and result.get("secure_url"):
                return result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload warning: {e}. Attempting fallback...")

    # 2. Try Local File Storage Fallback (for writable environments)
    try:
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        local_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file_storage.seek(0)
        file_storage.save(local_path)
        return f"/static/uploads/{unique_filename}"
    except (OSError, IOError) as e:
        print(f"Local storage not writable on serverless ({e}). Converting to base64 Data URI...")

    # 3. Serverless Base64 Data URI Fallback (guaranteed to work with MongoDB)
    try:
        file_storage.seek(0)
        content = file_storage.read()
        mimetype = getattr(file_storage, "mimetype", "") or "image/jpeg"
        encoded = base64.b64encode(content).decode("utf-8")
        return f"data:{mimetype};base64,{encoded}"
    except Exception as e:
        print(f"Base64 fallback failed: {e}")
        return None

