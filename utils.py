import smtplib
import secrets
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import student_collection

# Google auth
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

# --- SECURITY CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION")
ALGORITHM = "HS256"

# --- EMAIL CONFIGURATION ---
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")

# --- PASSWORD HASHING ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(password, hashed)

# --- JWT TOKEN MANAGEMENT ---
def create_token(data: dict) -> str:
    """Create JWT token"""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_student(token: str = Depends(oauth2_scheme)):
    """Get current student from JWT token"""
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

# --- EMAIL FUNCTIONS ---
def send_signup_email(recipient_email: str, password: str, student_name: str = "Student") -> bool:
    """Send signup confirmation email with password"""
    try:
        subject = "Welcome to Kerala Student Job Portal - Account Activated"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 20px; }}
                    .footer {{ background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d; }}
                    .password-box {{ background-color: #ecf0f1; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
                    .password-label {{ font-weight: bold; color: #2c3e50; }}
                    .password-value {{ font-family: monospace; font-size: 16px; background-color: white; padding: 10px; border-radius: 4px; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Kerala Student Job Portal</h1>
                        <p>Your Account Has Been Activated!</p>
                    </div>
                    <div class="content">
                        <p>Dear {student_name},</p>
                        <p>Welcome to the Kerala Student Job Portal! Your account has been successfully activated.</p>
                        
                        <p>Your login credentials are:</p>
                        <div class="password-box">
                            <div class="password-label">Email:</div>
                            <div class="password-value">{recipient_email}</div>
                            
                            <div class="password-label" style="margin-top: 15px;">Password:</div>
                            <div class="password-value">{password}</div>
                        </div>
                        
                        <p><strong>Important Security Notes:</strong></p>
                        <ul>
                            <li>Keep your password confidential</li>
                            <li>Change your password after your first login</li>
                            <li>Do not share this email with anyone</li>
                        </ul>
                        
                        <p>You can now login to your account and start exploring job opportunities tailored for Kerala students.</p>
                        
                        <p>If you have any issues, please contact our support team.</p>
                        
                        <p>Best regards,<br>Kerala Student Job Portal Team</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 Kerala Student Job Portal. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email
        message.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending signup email: {str(e)}")
        return False

def send_forgot_password_email(recipient_email: str, temporary_password: str, student_name: str = "Student") -> bool:
    """Send forgot password email with temporary password"""
    try:
        subject = "Password Reset Request - Kerala Student Job Portal"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
                    .header {{ background-color: #e74c3c; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 20px; }}
                    .footer {{ background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d; }}
                    .password-box {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #e74c3c; margin: 20px 0; }}
                    .password-label {{ font-weight: bold; color: #2c3e50; }}
                    .password-value {{ font-family: monospace; font-size: 16px; background-color: white; padding: 10px; border-radius: 4px; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset</h1>
                        <p>Password Reset Request</p>
                    </div>
                    <div class="content">
                        <p>Dear {student_name},</p>
                        <p>We received a password reset request for your account. If you did not make this request, please ignore this email.</p>
                        
                        <p>Your temporary password is:</p>
                        <div class="password-box">
                            <div class="password-label">Temporary Password:</div>
                            <div class="password-value">{temporary_password}</div>
                        </div>
                        
                        <p><strong>Instructions:</strong></p>
                        <ol>
                            <li>Use this temporary password to login to your account</li>
                            <li>Go to your profile settings and change your password immediately</li>
                            <li>Do not share this password with anyone</li>
                        </ol>
                        
                        <p>If you have issues, please contact our support team.</p>
                        
                        <p>Best regards,<br>Kerala Student Job Portal Team</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 Kerala Student Job Portal. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email
        message.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

def generate_temporary_password() -> str:
    """Generate a secure temporary password"""
    return secrets.token_urlsafe(12)


def verify_google_token(id_tok: str) -> dict:
    """Verify Google ID token and return payload"""
    try:
        request = google_requests.Request()
        idinfo = google_id_token.verify_oauth2_token(id_tok, request)
        # If you want to enforce client ID, set GOOGLE_CLIENT_ID env var
        CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        if CLIENT_ID and idinfo.get("aud") != CLIENT_ID:
            raise Exception("Invalid token audience")
        return idinfo
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
