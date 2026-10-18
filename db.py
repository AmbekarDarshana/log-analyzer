"""
db.py — Handles all communication with MongoDB.
Keeps database logic separate from web logic.
"""

from pymongo import MongoClient

# Connection details
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "log_analyzer_db"
COLLECTION_NAME = "logs"


def get_collection():
    """
    Connects to MongoDB and returns the logs collection.
    Think of this as "opening the correct filing cabinet drawer."
    """
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]


def save_logs(logs):
    """
    Takes a list of parsed log dictionaries and inserts them into MongoDB.
    Returns the count of inserted documents.
    """
    collection = get_collection()
    
    if not logs:
        return 0
    
    # insert_many() adds multiple documents at once (faster than one by one)
    result = collection.insert_many(logs)
    return len(result.inserted_ids)


def get_all_logs():
    """
    Returns ALL logs from the database, newest first.
    Used for the dashboard/view-all page.
    """
    collection = get_collection()
    
    # find() with no arguments = "give me everything"
    # sort by _id in descending order (-1) = newest first
    return list(collection.find().sort("_id", -1))


def get_log_counts():
    """
    Counts logs by level (INFO, WARN, ERROR).
    Returns a dictionary like: {"INFO": 15, "WARN": 3, "ERROR": 2}
    """
    collection = get_collection()
    
    counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
    
    # MongoDB aggregation pipeline - counts each level automatically
    pipeline = [
        {"$group": {
            "_id": "$level",      # Group by the 'level' field
            "count": {"$sum": 1}   # Count how many in each group
        }}
    ]
    
    results = collection.aggregate(pipeline)
    
    for result in results:
        level = result["_id"]
        count = result["count"]
        if level in counts:
            counts[level] = count
    
    return counts


def clear_all_logs():
    """
    Deletes all logs from the database.
    Useful for testing/resetting.
    """
    collection = get_collection()
    result = collection.delete_many({})
    return result.deleted_count