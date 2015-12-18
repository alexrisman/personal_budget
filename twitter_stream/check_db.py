from pymongo import MongoClient
client = MongoClient()

db = client.dealtrader
collection = db.raw_tweets

print collection
print collection.count()
print collection.find_one(sort=[("id",1)])
print collection.find_one(sort=[("id",-1)])
