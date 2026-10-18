from pymongo import MongoClient

# Connect to MongoDB running on your own computer
client = MongoClient("mongodb://localhost:27017/")

# Create (or switch to) a database called "log_analyzer_db"
db = client["log_analyzer_db"]

# Create (or switch to) a collection called "logs"
collection = db["logs"]

# Insert one test document
test_doc = {
    "timestamp": "2026-10-18 14:00:00",
    "level": "INFO",
    "message": "MongoDB connection test successful!"
}

result = collection.insert_one(test_doc)

print(f"✅ Inserted! Document ID: {result.inserted_id}")

# Read it back to confirm
found = collection.find_one({"level": "INFO"})
print(f"✅ Found in database: {found}")

# Clean up — delete the test document
collection.delete_one({"_id": result.inserted_id})
print("✅ Test document cleaned up")