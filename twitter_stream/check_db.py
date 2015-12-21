from pymongo import MongoClient
client = MongoClient()

db = client.dealtrader
collection = db.raw_tweets

print collection
print collection.count()
print collection.find_one(sort=[("id",1)])
print collection.find_one(sort=[("id",-1)])

pipe = [{"$group" : {'_id':{ '$substr': ["$created_at", 0, 10] }, 'count':{'$sum':1}}}]
grouping = collection.aggregate(pipeline=pipe)
print grouping
dates=[]
for row in grouping['result']:
    if row['_id'][4:7] == 'Dec':
        month = 12
    if row['_id'][4:7] == 'Nov':
        month = 11
    if row['_id'][4:7] == 'Oct':
        month = 10
    if row['_id'][4:7] == 'Sep':
        month = 9
    if row['_id'][4:7] == 'Aug':
        month = 8
    if row['_id'][4:7] == 'Jul':
        month = 7
    if row['_id'][4:7] == 'Jun':
        month = 6
    if row['_id'][4:7] == 'May':
        month = 5
    if row['_id'][4:7] == 'Apr':
        month = 4
    if row['_id'][4:7] == 'Mar':
        month = 3
    if row['_id'][4:7] == 'Feb':
        month = 2
    if row['_id'][4:7] == 'Jan':
        month = 1
    day = int(row['_id'][8:10])
    mapper = {'date': row['_id'], 'month': month, 'day': day,'count': row['count']}
    dates.append(mapper)

dates = sorted(dates, key=lambda k: (k['month'],k['day']) )
for date in dates:
    #print date
    pass