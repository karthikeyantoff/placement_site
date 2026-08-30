import sys
import os

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

app.secret_key = "placement_mgmt_super_secret_key_2026"
app.config["SECRET_KEY"] = "placement_mgmt_super_secret_key_2026"

# Vercel serverless entrypoint
application = app

