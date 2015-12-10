
from utils import load_credentials, tweepy_auth, tweepy_api, load_follow_list, print_follow_list, return_follow_id
import sys
import json
import pymongo
import argparse

def get_latest_id(tweeter_id):
    try:
        tweetsort = collection.find({"user_id": tweeter_id}).sort([("id", pymongo.ASCENDING)])
        first_id = tweetsort.next()['id']
        max_id = first_id-1
    except:
        first_id = None
        max_id = None
    return first_id, max_id

def add_latest_tweets(tweeter_id):
    tweets = api.user_timeline(user_id=tweeter_id,max_id=get_latest_id(tweeter_id)[1])
    if len(tweets) > 0:
        sys.stdout.write("adding tweets")
    for tweet in tweets:
        tweet = json.loads(json.dumps(tweet._json))
        raw_tweet= {"id":tweet['id'],
                    "user_id":tweet['user']['id'],
                    "screen_name":tweet['user']['screen_name'],
                    "created_at":tweet['created_at'],
                    "text":tweet['text']}
        collection.insert(raw_tweet, continue_on_error=True)
    try:
        add_latest_tweets(tweeter_id)
    except:
        sys.stdout.write("cant add tweets")
        return True

if __name__ == '__main__':
    client = pymongo.MongoClient()
    collection = client.dealtrader.raw_tweets
    collection.create_index([("id", pymongo.ASCENDING)], unique=True)

    credentials = load_credentials()
    auth = tweepy_auth(credentials, user=True)
    api = tweepy_api(auth)

    ap = argparse.ArgumentParser()
    ap.add_argument("-id", "--follow_id", required=False, default=False, help="Screen name to follow")
    args = vars(ap.parse_args())
    followid = args['follow_id']

    if followid:
        tweeter_id = return_follow_id(tweeter=followid)
        sys.stdout.write(tweeter_id)
        tweeter_id = int(tweeter_id)
        add_latest_tweets(tweeter_id)
    else:
        for tweeter in print_follow_list():
            sys.stdout.write(tweeter)
            tweeter_id = return_follow_id(tweeter=tweeter)
            sys.stdout.write(tweeter_id)
            tweeter_id = int(tweeter_id)
            add_latest_tweets(tweeter_id)
