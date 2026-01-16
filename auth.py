from fastapi import APIRouter, HTTPException, status, Depends
from database import new_users_collection, get_db
from models import SignupRequest, LoginRequest, NewUserSchema
from datetime import datetime
import bcrypt
import jwt

router = APIRouter()
SECRET_KEY = "your_secret_key"  # Use a secure key

@router.post("/signup")
async def signup(request: SignupRequest, db=Depends(get_db)):
    # Check if user already exists (allow new registrations)
    existing_user = await new_users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    # Hash password
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user (no pre-registration required)
    new_user = NewUserSchema(
        email=request.email,
        password=hashed_password.decode('utf-8'),
        course=request.course,
        phone_number=request.phone_number,
        signup_date=datetime.now().isoformat(),
        is_active=True
    )
    result = await new_users_collection.insert_one(new_user.dict(by_alias=True))
    
    # Generate token
    token = jwt.encode({"user_id": str(result.inserted_id)}, SECRET_KEY, algorithm="HS256")
    
    return {"message": "Signup successful", "token": token}

@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    # Find user
    user = await new_users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    
    # Generate token
    token = jwt.encode({"user_id": str(user["_id"])}, SECRET_KEY, algorithm="HS256")
    
    return {"message": "Login successful", "token": token}