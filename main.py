from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

# Import database and models
from database import student_collection, job_collection, close_db
from models import UserSchema, ForgotPasswordRequest, JobSchema, StudentSchema, SignupRequest, GoogleAuthRequest

# Import auth router from auth.py
from auth import router as auth_router

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

# Include auth router (replaces duplicate endpoints)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

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
            "signup": "/auth/signup (POST)",
            "login": "/auth/login (POST)",
            "forgot_password": "/forgot-password (POST)",
            "jobs": "/jobs (GET - requires authentication)",
        }
    }

# Removed duplicate auth endpoints (signup, login, google_auth) - now handled by auth.py router

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
