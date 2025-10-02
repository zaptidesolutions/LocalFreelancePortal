from passlib.context import CryptContext
from ..config.config_setup import db

# ---------------- Security Setup ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- MongoDB Setup ----------------
users_collection = db["users"]


# ---------------- Startup: Add default users ----------------
async def create_default_users():
    default_users = [
        {"username": "alice", "password": "alice123"},
        {"username": "bob", "password": "bob123"}
    ]
    
    for user in default_users:
        existing_user = await users_collection.find_one({"username": user["username"]})
        if not existing_user:
            hashed_password = pwd_context.hash(user["password"])
            await users_collection.insert_one({"username": user["username"], "hashed_password": hashed_password})
            print(f"Inserted default user: {user['username']}")
        else:
            print(f"User {user['username']} already exists")