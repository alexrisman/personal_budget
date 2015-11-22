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
            dealProduct = tweetText[:tweetText.index('$')-1]
            dealPrice = tweetText[tweetText.index('$')+1:tweetText.index(' ', tweetText.index('$'))]

            # search product in api
            f = finding()
            f.execute('findItemsAdvanced', {'keywords': dealProduct})
            dom = f.response_dom()
            items = dom.getElementsByTagName('item')

            for item in items:
                # pull in product description and price of search results from api
                marketProduct = item.getElementsByTagName('title')[0].firstChild.nodeValue
                marketPrice = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue

                # dump all matches
                with open('matches.csv','a') as matchCsv:
                    matchCsv.write(dealProduct + "," + dealPrice + "," + marketProduct + "," + marketPrice + "\n")

                # dump potential trades
                with open('trades.csv','a') as tradeCsv:
                    if float(marketPrice) > float(dealPrice):
                        print dealProduct + "," + dealPrice + "," + marketProduct + "," + marketPrice + "\n"
                        tradeCsv.write(dealProduct + "," + dealPrice + "," + marketProduct + "," + marketPrice + "\n")

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

    sapi = streaming.Stream(auth, CustomStreamListener(api))
    try:
        sapi.filter(follow=load_follow_list())
    except KeyboardInterrupt:
        print "Twitter streaming interrupted"
