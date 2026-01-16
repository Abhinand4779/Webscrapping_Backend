from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

# Import database and models
from database import student_collection, job_collection, close_db
from models import UserSchema, ForgotPasswordRequest, JobSchema, StudentSchema, SignupRequest, GoogleAuthRequest

# Import utilities
from utils import (
    hash_password,
    verify_password,
    create_token,
    get_current_student,
    send_signup_email,
    send_forgot_password_email,
    generate_temporary_password,
    verify_google_token,
)

# Initialize FastAPI app
app = FastAPI(
    title="Kerala Student Job Portal",
    description="Job portal for Kerala students",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# --- ENDPOINTS ---

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Kerala Student Job Portal API",
        "version": "1.0.0",
        "endpoints": {
            "signup": "/signup (POST)",
            "login": "/login (POST)",
            "forgot_password": "/forgot-password (POST)",
            "jobs": "/jobs (GET - requires authentication)",
        }
    }

@app.post("/signup", tags=["Authentication"])
async def signup(payload: SignupRequest):
    """
    Signup endpoint - Create account with email and password
    Student must be pre-registered by admin
    """
    student = await student_collection.find_one({"email": payload.email})
    
    if not student:
        raise HTTPException(
            status_code=403,
            detail="Email not registered. Only pre-registered students can activate accounts."
        )

    if student.get("password"):
        raise HTTPException(
            status_code=400,
            detail="Account already activated. Please login."
        )

    # Hash password and save; also store course if provided
    hashed_password = hash_password(payload.password)
    update_fields = {"password": hashed_password, "signup_date": datetime.utcnow()}
    if payload.course:
        # store the enum value string in DB
        update_fields["course"] = payload.course.value

    await student_collection.update_one(
        {"email": payload.email},
        {"$set": update_fields}
    )
    
    # Send confirmation email
    student_name = student.get("name", "Student")
    email_sent = send_signup_email(payload.email, payload.password, student_name)
    
    return {
        "message": "Account activated successfully",
        "email": payload.email,
        "email_status": "Confirmation email sent" if email_sent else "Account activated but email could not be sent"
    }

@app.post("/login", tags=["Authentication"])
async def login(user: UserSchema):
    """
    Login endpoint - Returns JWT token
    """
    student = await student_collection.find_one({"email": user.email})
    
    if not student or not student.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, student["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": student["email"], "role": "student"})

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": student["email"]
    }

@app.post("/auth/google", tags=["Authentication"])
async def google_auth(payload: GoogleAuthRequest):
    """Authenticate or register user using Google ID token"""
    # Verify Google ID token
    idinfo = verify_google_token(payload.id_token)
    email = idinfo.get("email")
    name = idinfo.get("name") or idinfo.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Google token did not contain an email")

    student = await student_collection.find_one({"email": email})

    if not student:
        # Create student record (allows Google sign-ins even if not pre-registered)
        new_student = {
            "email": email,
            "name": name,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        if payload.course:
            new_student["course"] = payload.course.value
        await student_collection.insert_one(new_student)
    else:
        # update name/course if provided
        update = {}
        if name and not student.get("name"):
            update["name"] = name
        if payload.course:
            update["course"] = payload.course.value
        if update:
            await student_collection.update_one({"email": email}, {"$set": update})

    token = create_token({"sub": email, "role": "student"})
    return {"access_token": token, "token_type": "bearer", "email": email}

@app.post("/forgot-password", tags=["Authentication"])
async def forgot_password(request: ForgotPasswordRequest):
    """
    Forgot password endpoint - Send temporary password via email
    """
    student = await student_collection.find_one({"email": request.email})
    
    if not student:
        # Security: Don't reveal if email exists
        return {"message": "If the email exists, a password reset link will be sent shortly"}
    
    # Generate and hash temporary password
    temporary_password = generate_temporary_password()
    hashed_password = hash_password(temporary_password)
    
    # Update password in database
    await student_collection.update_one(
        {"email": request.email},
        {"$set": {"password": hashed_password, "password_reset_date": datetime.utcnow()}}
    )
    
    # Send email
    student_name = student.get("name", "Student")
    email_sent = send_forgot_password_email(request.email, temporary_password, student_name)
    
    return {
        "message": "If the email exists, a password reset link will be sent shortly",
        "email_status": "Password reset email sent" if email_sent else "Could not send email"
    }

@app.get("/jobs", response_model=List[JobSchema], tags=["Jobs"])
async def get_jobs(current_student=Depends(get_current_student)):
    """
    Get all jobs - Requires authentication
    """
    # Filter jobs by student's course/domain if available
    student_course = current_student.get("course") if isinstance(current_student, dict) else None
    if student_course:
        query = {"$or": [{"category": student_course}, {"source": student_course}]}
        jobs = await job_collection.find(query).to_list(100)
    else:
        jobs = await job_collection.find().to_list(100)
    return jobs

@app.get("/profile", response_model=StudentSchema, tags=["Profile"])
async def get_profile(current_student=Depends(get_current_student)):
    """
    Get current student profile - Requires authentication
    """
    return current_student

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
