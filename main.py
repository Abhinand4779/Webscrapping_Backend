from fastapi import FastAPI, Body, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from bson import ObjectId
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os

app = FastAPI(title="Kerala Student Job Portal")

# --- CONFIGURATION ---
MONGO_URI = "mongodb+srv://hudavkd1:hudanawrin@cluster0.6jjjf37.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
SECRET_KEY = "CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION"
ALGORITHM = "HS256"

# --- SECURITY UTILS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# --- DATABASE CONNECTION ---
client = AsyncIOMotorClient(MONGO_URI)
db = client.student_job_portal
job_collection = db.get_collection("scraped_jobs")
student_collection = db.get_collection("students")

# --- MODELS ---
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

# --- AUTH HELPERS ---
async def get_current_student(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        student = await student_collection.find_one({"email": email})
        if not student:
            raise HTTPException(status_code=403, detail="Access denied")
            
        return student
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- ROUTES ---

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Kerala Student Job Portal API"}

@app.post("/signup", tags=["Authentication"])
async def signup(user: UserSchema):
    # Check if student exists in database (pre-registered by admin)
    student = await student_collection.find_one({"email": user.email})
    
    if not student:
        raise HTTPException(
            status_code=403,
            detail="Email not registered. Only pre-registered students can activate accounts."
        )

    # Check if already activated
    if student.get("password"):
        raise HTTPException(
            status_code=400,
            detail="Account already activated. Please login."
        )

    # Update with hashed password
    await student_collection.update_one(
        {"email": user.email},
        {"$set": {"password": hash_password(user.password)}}
    )
    
    return {"message": "Account activated successfully"}

@app.post("/login", tags=["Authentication"])
async def login(user: UserSchema):
    student = await student_collection.find_one({"email": user.email})
    
    if not student or not student.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, student["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "sub": student["email"],
        "role": "student"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/jobs", response_model=List[JobModel], tags=["Jobs"])
async def get_jobs(current_student=Depends(get_current_student)):
    jobs = await job_collection.find().to_list(100)
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)