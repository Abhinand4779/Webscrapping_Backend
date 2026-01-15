from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class JobSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    company: str
    location: str
    salary: Optional[str] = "Not Disclosed"
    description: Optional[str] = ""
    link: str
    source: str  # e.g., 'LinkedIn', 'Indeed'

    class Config:
        json_encoders = {ObjectId: str}