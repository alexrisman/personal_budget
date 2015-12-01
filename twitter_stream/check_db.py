from pymongo import MongoClient
client = MongoClient()

db = client.dealtrader
collection = db.raw_tweets

print collection.count()
print collection.find_one()
