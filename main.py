from fastapi import FastAPI, Body, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from bson import ObjectId

app = FastAPI(title="Kerala Student Job Portal")

# --- DATABASE CONNECTION ---
MONGO_URI = "mongodb+srv://hudavkd1:hudanawrin@cluster0.6jjjf37.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client.student_job_portal
job_collection = db.get_collection("scraped_jobs")

# --- FIX FOR OPENAPI ERROR ---
# This helper ensures MongoDB's _id is converted to a string for the API docs
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

# --- MODELS ---
class JobModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    company: str
    location: str
    link: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserSchema(BaseModel):
    email: EmailStr
    password: str

# --- ROUTES ---

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Kerala Student Job Portal API"}

@app.post("/signup", tags=["Authentication"])
async def signup(user: UserSchema):
    # Add your logic to save user to DB here
    return {"message": "User created successfully"}

@app.post("/login", tags=["Authentication"])
async def login(user: UserSchema):
    return {"message": "Login successful"}

@app.get("/jobs", response_model=List[JobModel], tags=["Jobs"])
async def get_jobs():
    jobs = await job_collection.find().to_list(100)
    return jobs