import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["aerovision_db"]

print("--- 1. Event Type ---")
for doc in db.events.aggregate([{ "$group": { "_id": "$event_type", "total": { "$sum": 1 } } }, { "$sort": { "total": -1 } }]):
    print(doc)

print("\n--- 2. Avg Response by Mode ---")
for doc in db.events.aggregate([{ "$group": { "_id": "$mode", "avg_response_ms": { "$avg": "$response_ms" } } }, { "$sort": { "avg_response_ms": -1 } }]):
    print(doc)

print("\n--- 3. Severity ---")
for doc in db.events.aggregate([{ "$group": { "_id": "$severity", "total": { "$sum": 1 } } }, { "$sort": { "total": -1 } }]):
    print(doc)

print("\n--- 4. Slow Stops ---")
for doc in db.events.aggregate([{ "$match": { "event_type": "Safety Stop", "response_ms": { "$gt": 130 } } }, { "$count": "slow_stops" }]):
    print(doc)
