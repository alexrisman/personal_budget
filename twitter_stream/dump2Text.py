#! /usr/bin/env python27
# DK 9 Dec 2015
# dump a bunch of tweets to a text file for analysis, using pymongo's json util

from pymongo import MongoClient
from bson import Binary, Code
from bson.json_util import dumps

client = MongoClient()

db = client.dealtrader

collection = db.raw_tweets

with open('tweetDump_1.txt','w') as f:
    for t in xrange(0, collection.count()):
        tweet = collection.find()[t]
        f.write(dumps(tweet) + '\n')

