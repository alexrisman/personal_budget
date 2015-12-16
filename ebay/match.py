#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import load_credentials, tweepy_auth, tweepy_api, load_follow_list
from tweepy import streaming, StreamListener
from os import environ
import sys
import json

# pwd = environ['MONGOPWD']

import ebaysdk
from ebaysdk.finding import Connection as finding

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
            dealProduct = dealProduct.replace(",", " ")
            dealPrice = tweetText[tweetText.rfind('$')+1:tweetText.index(' ', tweetText.rfind('$'))]

            # search product in api
            f = finding()
            f.execute('findItemsAdvanced', {'keywords': dealProduct})
            dom = f.response_dom()
            items = dom.getElementsByTagName('item')

            for item in items:
                bidCount = ""
                positiveFeedbackPercent = ""
                # pull in product description and price of search results from api
                marketProduct = item.getElementsByTagName('title')[0].firstChild.nodeValue
                marketProduct = marketProduct.replace(",", " ")
                marketPrice = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue
                timeLeft = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('timeLeft')[0].firstChild.nodeValue
                if len(item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('bidCount')) > 0: bidCount = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('bidCount')[0].firstChild.nodeValue
                if len(item.getElementsByTagName('sellerInfo')) > 0: positiveFeedbackPercent = item.getElementsByTagName('sellerInfo')[0].getElementsByTagName('positiveFeedbackPercent')[0].firstChild.nodeValue
                hoursLeft = 0.0
                if "DT" in timeLeft and "H" in timeLeft and "M" in timeLeft:
                    timeLeft = timeLeft[1:-1]
                    days = timeLeft.split("DT")[0]
                    hours = timeLeft.split("DT")[1].split("H")[0]
                    minutes = timeLeft.split("DT")[1].split("H")[1].split("M")[0]
                    #print days + " " + hours +  " " + minutes
                    hoursLeft = float(days) * 24 + float(hours) + float(minutes) / 60

                # dump all matches
                with open('matches.csv','a') as matchCsv:
                    print tweetText + "," + dealProduct + "," + str(dealPrice) + "," + str(marketProduct) + "," + str(marketPrice) + "," + str(hoursLeft) + "," + str(bidCount) + "," + str(positiveFeedbackPercent) + "\n"
                    matchCsv.write(tweetText + "," + dealProduct + "," + str(dealPrice) + "," + str(marketProduct) + "," + str(marketPrice) + "," + str(hoursLeft) + "," + str(bidCount) + "," + str(positiveFeedbackPercent) + "\n")

                # dump potential trades
                with open('trades.csv','a') as tradeCsv:
                    if float(marketPrice) > float(dealPrice):
                        print "TRADE: " + tweetText + "," + dealProduct + "," + dealPrice + "," + marketProduct + "," + marketPrice + "," + str(hoursLeft) + "," + str(bidCount) + "," + str(positiveFeedbackPercent) + "\n"
                        tradeCsv.write(tweetText + "," + dealProduct + "," + str(dealPrice) + "," + marketProduct + "," + str(marketPrice) + "," + str(hoursLeft) + "," + str(bidCount) + "," + str(positiveFeedbackPercent) + "\n")
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
    with open('matches.csv','a') as matchCsv:
        matchCsv.write("Tweet,DealProduct,DealPrice,MarketProduct,MarketPrice,HoursLeft,BidCount,PositiveFeedbackPct\n")
    with open('trades.csv','a') as tradeCsv:
        tradeCsv.write("Tweet,DealProduct,DealPrice,MarketProduct,MarketPrice,HoursLeft,BidCount,PositiveFeedbackPct\n")
    sapi = streaming.Stream(auth, CustomStreamListener(api))
    try:
        sapi.filter(follow=load_follow_list())
    except KeyboardInterrupt:
        print "Twitter streaming interrupted"
    except UnicodeError:
        print "Unicode error"
        sapi.filter(follow=load_follow_list())
