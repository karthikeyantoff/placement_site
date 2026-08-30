import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock
from config import Config

import certifi

_db = None
_client = None

def get_db():
    global _db, _client
    if _db is not None:
        return _db
    
    mongo_uri = Config.MONGO_URI
    db_name = Config.DB_NAME
    
    # Try connecting to live MongoDB
    try:
        ca = certifi.where()
        _client = MongoClient(mongo_uri, tlsCAFile=ca, serverSelectionTimeoutMS=4000)
        # Verify connection
        _client.admin.command('ping')
        _db = _client[db_name]
        print(f"Connected to Live MongoDB at {mongo_uri}")
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
        print(f"Live MongoDB not available ({e}). Initializing In-Memory MongoMock for local environment...")
        _client = mongomock.MongoClient()
        _db = _client[db_name]
        print("Connected to In-Memory MongoMock successfully!")
        
    init_indexes(_db)
    auto_seed_if_empty(_db)
    return _db

def init_indexes(db):
    try:
        db.users.create_index("username", unique=True)
        db.students.create_index("reg_number", unique=True)
        db.companies.create_index("company_name")
        db.notifications.create_index("receiver")
        db.placements.create_index("reg_number")
        db.resume_scores.create_index([("student_id", 1), ("jd_title", 1)])
    except Exception as e:
        print(f"Note on index creation: {e}")

def auto_seed_if_empty(db):
    if db.users.count_documents({}) == 0:
        print("Database is empty. Running auto-seeding...")
        try:
            from seed_data import seed_database
            seed_database(db)
        except Exception as e:
            print(f"Auto-seeding error: {e}")
