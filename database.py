from motor.motor_asyncio import AsyncIOMotorClient

# Replace with your actual MongoDB URI
MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient("mongodb+srv://hudavkd1:hudanawrin@cluster0.6jjjf37.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
database = client.student_job_portal
job_collection = database.get_collection("scraped_jobs")