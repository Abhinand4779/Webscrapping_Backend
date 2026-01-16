from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB Configuration
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://hudavkd1:hudanawrin@cluster0.6jjjf37.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Initialize MongoDB Client
client = AsyncIOMotorClient(MONGO_URI)
database = client.student_job_portal

# Collections
job_collection = database.get_collection("scraped_jobs")
student_collection = database.get_collection("students")
new_users_collection = database.get_collection("new_users")  # New collection for job placement

# Dependency for getting database
def get_db():
    return database

async def close_db():
    """Close database connection"""
    client.close()
