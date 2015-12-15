#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import load_credentials, tweepy_auth, tweepy_api, load_follow_list
from tweepy import streaming, StreamListener
from os import environ
import sys
import json
import time
import datetime

# pwd = environ['MONGOPWD']

import ebaysdk
from ebaysdk.finding import Connection as finding
from twython import Twython

class CustomStreamListener(StreamListener):
    def __init__(self, api):
        self.api = api
        self.count = 0
        super(StreamListener, self).__init__()
        self.counter = 0
    
    def on_data(self, tweet):
        tweetJson = json.loads(tweet)
        tweetText = tweetJson['text']
        if '$' in tweetText and "Win a" not in tweetText and "Lightning Deal!" not in tweetText:
            # parse product description and price from tweet
            dealProduct = tweetText[:tweetText.rfind('$')-1]
            dealProduct = str(dealProduct).replace(",", " ")
            dealPrice = tweetText[tweetText.rfind('$')+1:tweetText.index(' ', tweetText.rfind('$'))]

            # search product in api
            f = finding()
            f.execute('findItemsAdvanced', {'keywords': dealProduct})
            dom = f.response_dom()
            items = dom.getElementsByTagName('item')

            numListings = 0.0
            marketPriceLow = 99999.99
            marketPriceAvg = 0.0
            shippingCost = 0.0
            if "Free Shipping" not in tweetText: shippingCost = 8.0
            for item in items:
                marketPrice = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue

                if float(marketPrice) > (float(dealPrice) + shippingCost):
                    numListings += 1.0
                    if float(marketPrice) < float(marketPriceLow): marketPriceLow = float(marketPrice)
                    marketPriceAvg += float(marketPrice)

            dealRating = 0
            if numListings > 0.0:
                marketPriceAvg = marketPriceAvg / numListings
                if float(marketPriceLow) > (float(dealPrice) + shippingCost) and marketPriceLow != 99999.99:
                    if numListings >= 25: dealRating = 5
                    elif numListings >= 10: dealRating = 4
                    elif numListings >= 5: dealRating = 3

                if float(marketPriceAvg) > (float(dealPrice) + shippingCost):
                    if numListings >= 10: dealRating = 2
                    elif numListings >= 5: dealRating = 1

                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                # dump potential trades
                with open('dealRating.csv','a') as dealRatingDump:
                    print "DealRating: " + str(dealRating) + "/5 stars : " + tweetText + "," + dealProduct + "," + dealPrice + "," + str(marketPriceAvg) + "," + str(marketPriceLow) + "," + str(int(numListings)) + "," + str(st) + "\n"
                    dealRatingDump.write(tweetText + "," + dealProduct + "," + dealPrice + "," + str(marketPriceAvg) + "," + str(marketPriceLow) + "," + str(int(numListings)) + "," + str(st) + "," + str(dealRating) + "\n")

                pubTweet = Twython("1Oqu7GYy9RVUGgATxdsC6IDBH", "VjSUMkJaRJkadurzCyJ8mIl05izjdYz9nXzklgyRqfIou2WN1M", "4564439173-DyQWKd8smdv1mP70qoyGynICpPdkUTUeMCxh7qy", "3OfiZcD6RcaqvjDkiQBc50EzkQ9jr3FOTNJ8T3qUcFvfj")
                pubTweet.update_status(status="DealRating: " + str(dealRating) + "/5 stars : " + tweetText)

        return True

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

if __name__ == '__main__':
    credentials = load_credentials()
    auth = tweepy_auth(credentials, user=True)
    api = tweepy_api(auth)

    print 'Running streamer'
    with open('dealRating.csv','a') as dealRatingDump:
        dealRatingDump.write("Tweet,DealProduct,DealPrice,MarketPriceAvg,MarketPriceLow,Listings,Timestamp,DealRating\n")
    sapi = streaming.Stream(auth, CustomStreamListener(api))
    try:
        sapi.filter(follow=load_follow_list())
    except KeyboardInterrupt:
        print "Twitter streaming interrupted"
    except UnicodeError:
        print "Unicode error"
        sapi.filter(follow=load_follow_list())
    except UnicodeDecodeError:
        print "UnicodeDecode error"
        sapi.filter(follow=load_follow_list())
