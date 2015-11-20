#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import load_credentials, tweepy_auth, tweepy_api, load_follow_list
from tweepy import streaming, StreamListener
from os import environ
import sys
import json
import pymongo
import argparse

class CustomStreamListener(StreamListener):
    def __init__(self, api, verbose=False):
        self.api = api
        self.count = 0
        super(StreamListener, self).__init__()
        self.counter = 0
        self.verbose = verbose
        self.client = pymongo.MongoClient()
        self.collection = self.client.dealtrader.tweets
        self.create_index()
        self.log('Streaming started... counting tweets...')
    
    def on_data(self, tweet):
        try:
            tweet = json.loads(tweet)
            self.log(self.counter)
            self.collection.insert(tweet, continue_on_error=True)
            self.counter +=1
        except:
            self.log("database error but streamer will continue")
        return True

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

    def create_index(self):
        self.log("creating primary key")
        self.collection.create_index(
            [("id", pymongo.ASCENDING)],
            unique=True)

    def log(self, message):
        if self.verbose:
            print message

if __name__ == '__main__':
    credentials = load_credentials()
    auth = tweepy_auth(credentials, user=True)
    api = tweepy_api(auth)

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", required=False, type=bool, default=False, help="Set verbose output")
    args = vars(ap.parse_args())
    verbose = args['verbose']
    print 'Running streamer, verbose = %s' % verbose

    sapi = streaming.Stream(auth, CustomStreamListener(api, verbose=verbose))
    try:
        sapi.filter(follow=load_follow_list())
    except KeyboardInterrupt:
        print "Twitter streaming interrupted"
