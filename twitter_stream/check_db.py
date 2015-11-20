from pymongo import MongoClient
client = MongoClient()

db = client.dealtrader
collection = db.tweets

print collection.count()
print collection.find_one()
