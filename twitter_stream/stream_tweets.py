#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import load_credentials, tweepy_auth, tweepy_api, load_follow_list
from tweepy import streaming, StreamListener
from os import environ
import sys
import json

# pwd = environ['MONGOPWD']


class CustomStreamListener(StreamListener):
    def __init__(self, api):
        self.api = api
        self.count = 0
        super(StreamListener, self).__init__()
        self.counter = 0
    
    def on_data(self, tweet):
        print "zomg a tweet"
        with open('deal_tweets.txt','a') as outfile:
            outfile.write(tweet)
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
