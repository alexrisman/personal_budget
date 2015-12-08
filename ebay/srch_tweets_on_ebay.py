import pickle
import numpy as np
import re
import pandas as pd
import os
import sqlite3
from pymongo import MongoClient
import ebaysdk
from ebaysdk.finding import Connection as finding
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine


def cosDist(s1, s2):
    returnDist = 1
    try:
        vecs = TfidfVectorizer().fit_transform([s1,s2]).todense()
        cosDist = cosine(vecs[0], vecs[1])
        if not np.isnan(cosDist):
            returnDist = cosDist 
    except:
        pass
    return returnDist

def insert_data(cur, tname, data):
	rtnCode = 0
	try:
		data = list(map(lambda x : str(x).replace("'", "''"), data))
		data_string = "','".join(data)
		query = 'insert into ' + tname + " values ('" + data_string + "')"
		cur.execute(query)
	except:
		rtnCode = 1
	return rtnCode

with open("../ecommerce/model/nameModel.pickle", 'rb') as f:
    nameModel = pickle.load(f)

tweets = pickle.load(open('some_tweets.pickle', 'rb'))
lightning_deals = list(filter(lambda x : "Lightning Deal" in x['text'], tweets))
extracted = {}
for lightning_deal in lightning_deals:
	deal = lightning_deal['text']
	tweet_id = lightning_deal['id']
	tweet_ts = lightning_deal['created_at']
	try:
		deal_arr_1 = deal.split('! $')
		deal_arr_2 = deal_arr_1[1].split(' - ')
		deal_arr_3 = deal_arr_2[1].split(' http')
		price = float(deal_arr_2[0])
		product = deal_arr_3[0]
		extracted[product] = {'amazon_price': price, 'tweet_id': tweet_id, "tweet_ts": tweet_ts}
	except:
		pass

db_name = 'tweet_to_ebay.db'
try:
	os.remove(db_name)
except OSError:
	pass

conn = sqlite3.connect(db_name)
cur = conn.cursor()
table = 'tweets_to_ebay'
query = 'create table ' + table + ' (tweet_id, tweet_ts, amazon_name, amazon_price, ebay_name, ebay_price)'
cur.execute(query)
errorProducts = []
for product in extracted:
	product_tweet_dict = extracted[product]
	amazon_price = product_tweet_dict['amazon_price']
	tweet_id = product_tweet_dict['tweet_id']
	tweet_ts = product_tweet_dict['tweet_ts']
	f = finding()
	f.execute('findItemsAdvanced', {'keywords': product})
	dom = f.response_dom()

	items = dom.getElementsByTagName('item')[:10]
	candidates = {}

	for item in items:
	    ebayName = item.getElementsByTagName('title')[0].firstChild.nodeValue
	    ebayPrice = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue
	    cos = cosDist(product, ebayName)
	    pred = nameModel.predict([cos])[0]
	    if pred == 1:
	    	rtnCode = insert_data(cur, table, [tweet_id, tweet_ts, product, amazon_price, ebayName, ebayPrice])
	    	if rtnCode == 1:
	    		errorProducts.append(product)
conn.commit()
conn.close()
print(errorProducts)
	    

	    