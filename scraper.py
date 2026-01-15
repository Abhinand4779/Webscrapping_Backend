from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import jwt, JWTError
import pandas as pd

# ----------------------------
# APP
# ----------------------------
app = FastAPI(title="Kerala Student Job Portal")

# ----------------------------
# MONGODB
# ----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["job_portal"]
students_col = db["students"]

# ----------------------------
# SECURITY
# ----------------------------
SECRET_KEY = "CHANGE_THIS_SECRET_KEY"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ----------------------------
# MODELS
# ----------------------------
class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ----------------------------
# PASSWORD UTILS
# ----------------------------
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ----------------------------
# AUTH HELPERS
# ----------------------------
def get_current_student(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        student = students_col.find_one({
            "email": email,
            "is_active": True
        })

        if not student:
            raise HTTPException(status_code=403, detail="Access denied")

        return student

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------------------
# SIGNUP (ONLY PRE-REGISTERED)
# ----------------------------
@app.post("/signup")
def signup(data: SignupRequest):
    student = students_col.find_one({"email": data.email})

    if not student:
        raise HTTPException(
            status_code=403,
            detail="Email not registered. Contact admin."
        )

    if student.get("password"):
        raise HTTPException(
            status_code=400,
            detail="Account already activated. Please login."
        )

    students_col.update_one(
        {"email": data.email},
        {"$set": {"password": hash_password(data.password)}}
    )

    return {"message": "Account activated successfully"}

# ----------------------------
# LOGIN
# ----------------------------
@app.post("/login")
def login(data: LoginRequest):
    student = students_col.find_one({"email": data.email})

    if not student or not student.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, student["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "sub": student["email"],
        "role": "student"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ----------------------------
# JOB DATA (TEMP DATA)
# ----------------------------
jobs_df = pd.DataFrame([
    {
        "title": "Python Developer",
        "company": "Kerala Tech",
        "location": "Kochi",
        "category": "Python"
    },
    {
        "title": "React Developer",
        "company": "Startup Hub",
        "location": "Trivandrum",
        "category": "Frontend"
    },
    {
        "title": "UI/UX Designer",
        "company": "Design Studio",
        "location": "Calicut",
        "category": "UI/UX"
    }
])

# ----------------------------
# PROTECTED JOB API
# ----------------------------
@app.get("/jobs")
def get_jobs(student=Depends(get_current_student)):
    return jobs_df.to_dict(orient="records")

# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {
        "message": "Kerala Student Job Portal API",
        "login": "/login",
        "signup": "/signup",
        "jobs": "/jobs (requires login)"
    }

# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scraper:app", host="127.0.0.1", port=8000, reload=True)
