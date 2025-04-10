from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional , List
from fastapi import HTTPException

from dto.CreateAccountRequest import CreateAccountRequest
from dto.LoginRequest import LoginRequest

# MongoDB Configuration
MONGO_URI = "mongodb+srv://gauravkakad2468:gauravkakad2468@codeforsight.ox3cf.mongodb.net/?retryWrites=true&w=majority&appName=codeforsight"
client = None
db = None

# Collections
users_collection = None
conversations_collection = None
messages_collection = None
images_collection = None

async def initialize_database():
    global client, db, users_collection, conversations_collection, messages_collection, images_collection
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.codeforsight
    users_collection = db.users
    conversations_collection = db.conversations
    messages_collection = db.messages
    images_collection = db.images
    print("Database initialized successfully")

    
# Database Functions
async def insert_user(user: CreateAccountRequest):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    result = await users_collection.insert_one(user.dict())
    print(str(result))
    print(str(result.inserted_id))
    return str(result.inserted_id)

async def check_login(user: LoginRequest):
    user_data = await users_collection.find_one({"username": user.username, "password": user.password})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print(str(user_data))
    print(str(user_data["_id"]))
    return user_data
    # return str(user_data["_id"])

async def insert_conversation(user_id: str, conversation_name: str):
    result = await conversations_collection.insert_one({
        "user_id": user_id,
        "conversation_name": conversation_name,
        "timestamp": datetime.now()
    })
    return str(result.inserted_id)

async def update_conversation(conversation_id: str, conversation_name: str):
    result = await conversations_collection.update_one(
        {"_id": conversation_id},
        {"$set": {"conversation_name": conversation_name}}
    )
    return result.modified_count

async def insert_message(conversation_id: str, sender_id: str, message: str , isExplanation: Optional[bool] = 0 , isDotCode:Optional[bool] = 0  , isImage:Optional[bool] = 0 , img_id: Optional[str] = None):
    result = await messages_collection.insert_one({
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "message": message,
        "timestamp": datetime.now(),
        "isExplanation": isExplanation,
        "isDotCode": isDotCode,
        "isImage": isImage,
        "img_id": img_id

    })
    return str(result.inserted_id)

async def insert_image(user_id: str, conversation_id: str, image_base64: str):
    result = await images_collection.insert_one({
        "user_id": user_id,
        "conversation_id": conversation_id,
        "image_base64": image_base64,
        "timestamp": datetime.now()
    })
    return str(result.inserted_id)

async def get_all_conversations(user_id: str) -> List[dict]:
    conversations = await conversations_collection.find({"user_id": user_id}).to_list(length=100)
    return [{"id": str(c["_id"]), "conversation_name": c["conversation_name"]} for c in conversations]

async def get_all_messages(conversation_id: str) -> List[dict]:
    messages = await messages_collection.find({"conversation_id": conversation_id}).to_list(length=100)
    return [{
        "id": str(m["_id"]),
        "message": m["message"],
        "timestamp": m["timestamp"],
        "sender_id": m["sender_id"],
        "conversation_id": m["conversation_id"],
        "isExplanation": m["isExplanation"],
        "isDotCode": m["isDotCode"],
        "isImage": m["isImage"],
        "img_id": m["img_id"]
        } for m in messages]