from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from enum import Enum

# --- OBJECT ID MODEL ---
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

# --- JOB SCHEMA ---
class JobSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    company: str
    location: str
    category: Optional[str] = None
    salary: Optional[str] = "Not Disclosed"
    description: Optional[str] = ""
    link: str
    source: str  # e.g., 'LinkedIn', 'Indeed'

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# --- AUTHENTICATION SCHEMAS ---
class UserSchema(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CourseEnum(str, Enum):
    DIGITAL_MARKETING = "Digital Marketing"
    FLUTTER = "Flutter"
    REACT = "React"
    UI_UX = "UI/UX"
    MERN = "MERN"
    DJANGO = "Django"
    FASTAPI = "FastAPI"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    course: Optional[CourseEnum] = None

class GoogleAuthRequest(BaseModel):
    id_token: str
    course: Optional[CourseEnum] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# --- STUDENT SCHEMA ---
class StudentSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    course: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    signup_date: Optional[str] = None
    password_reset_date: Optional[str] = None
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
