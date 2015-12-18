#! /usr/bin/env python27
#
# created 10 dec 2015 DK for W210 Capstone project 

# imports
from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, Numeric, String, DateTime, ForeignKey, create_engine, BigInteger
from sqlalchemy import insert
import nltk
from pymongo import MongoClient
import sys
import ast
import re
from bson import Binary, Code
from bson.json_util import dumps

from ebayUtility import *


# Create a SQLite db using sqlalchemy
def init_db():
    # create a new metadata object
    metadata = MetaData()
    # build our tweets table
    tweets = Table('deals', metadata, 
              Column('deal_id', Integer(), primary_key=True),
              Column('price', String(15)),
              Column('url', String(255)),
              Column('description', String(255)),
              Column('tweet_id', BigInteger()),
              Column('analyzed', DateTime(), default=datetime.now),
              Column('updated', DateTime(), default=datetime.now, onupdate=datetime.now)
               )
    # build our matches table
    price_check_history = Table('price_check_history', metadata, 
              Column('match_id', Integer(), primary_key=True),
              Column('merchant', String(75)),
              Column('url', String(255)),
              Column('merchant_description', String(255)),
              Column('tweet_id', BigInteger()),
              Column('merchant_price', BigInteger()),
              Column('analyzed', DateTime(), default=datetime.now),
              Column('updated', DateTime(), default=datetime.now, onupdate=datetime.now)
               )   
    # now make a new file based SQLite3 db
    engine = create_engine('sqlite:///tweet.db')
    # and build it
    metadata.create_all(engine)
    # return the handle so we can talk to it
    return engine, tweets, price_check_history

# create a regular expression parser intended to pull out a PRICE and a DESCRIPTION from a tweet
def init_parser():
    # define a grammar with a PRICE object as a currency symbol and a number
    # and a DESCRiption as a series of adjectives nouns and verbs
    grammar = r"""
PRICE: {<\$><CD.*>+}
DESCR: {<DT|JJ|CD|VBG|VBD|NN|NNP.*>+<CC|NNP|NN>+}
"""
    # initialize the parser
    tp = nltk.RegexpParser(grammar)
    # and return it so we can use it below
    return tp


# Now we can actually do something
def main():
    # First create the SQL db that we will dump to
    engine, table, match_table = init_db()
    
    # and create a connection to it
    connection = engine.connect()
    
    # Now set up the parser
    parser = init_parser()
    
    # create a connection to the mongo DB
    client = MongoClient()

    # and get access to the contents
    db = client.dealtrader


    lastId = 0
    while True:
        collection = db.raw_tweets
        currInd = collection.count() - 1

        # pull the number of records to skip from the command line
        # should catch this and fail gracefully if not there
        
        tweet = collection.find()[currInd]
        # this should be a dictionary
        td = ast.literal_eval(dumps(tweet))
        # get the ID field
        tid = td['id']
        if tid != lastId:
            lastId = tid
            # and the text description
            desc = td['text']
            # this pattern, originally due to John Gruber, is supposed to match most URLs
            pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            # use a conventional regex to find the URLs -- there may be more than one
            urls = re.findall(pattern, desc)
            # get the URL characters out so as not to confuse the parser unduly
            remainder = re.sub(pattern, '', desc)
            # need to remove the words "Lightning Deal!" as well -- looks like a NP
            remainder = re.sub("Lightning Deal!", '', remainder)
            # and parse what's left
            # Try to speed this up -- replace it with a simple regex 
            re1='.*?'	# Non-greedy match on filler
            re2='(\\$[0-9]+(?:\\.[0-9][0-9])?)(?![\\d])'	# Dollar Amount 1

            rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
            m = rg.search(remainder)
            if m:
                itemprice = m.group(1)
                remainder = re.sub(re.escape(itemprice), '', remainder)
            else:
                tree = parser.parse(nltk.pos_tag(nltk.word_tokenize(remainder)))
                # go through the tree and look for the price and description
                # if there is more than one price, this will delete all of them and keep the last
                for obj in nltk.tree.Tree.subtrees(tree):
                    if obj.label() == 'PRICE':
                        itemprice = ''.join([w for w, wtype in obj.leaves()])
                        remainder = re.sub(re.escape(itemprice), '', remainder)
            # reparse the remainder
            tree = parser.parse(nltk.pos_tag(nltk.word_tokenize(remainder)))
            for obj in nltk.tree.Tree.subtrees(tree):
                if obj.label() == 'DESCR':
                    itemdescr = ' '.join([w for w, wtype in obj.leaves()])
            #print "{0}: {1} for {2}".format(urls, itemdescr, itemprice)
            # use this as a proxy for the success of the parsing step
            if len(urls) > 0:
                # rip out the punctuation and use the rest of the string if what the parser found is too short
                itemdescr = remainder.translate(string.maketrans("",""), string.punctuation)
                itemdescr = re.sub("Free|Shipping|Ship", "", itemdescr)
                ins = insert(table).values(
                            price = itemprice,
                            description = itemdescr,
                            url = urls[0],
                            tweet_id = tid
                            )
                result = connection.execute(ins)
            # dump the primary key so we can verify the insert
                print "parsed tweet successfully recorded with id:"
                print result.inserted_primary_key

                # search for matching ebay products
                try:
                    print "searching for matching ebay products"
                    items = getEbayItems(itemdescr)
                    if len(items) > 0:
                        print "found " + str(len(items)) + " potential matches"
                    for item in items:
                        try:
                            # only look at listings for new items (condition code 1000)
                            ebayConditionId = int(item.getElementsByTagName('condition')[0].getElementsByTagName('conditionId')[0].firstChild.nodeValue)
                            if ebayConditionId == 1000:
                                ebayName = item.getElementsByTagName('title')[0].firstChild.nodeValue
                                ebayPrice = item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue
                                ebayURL = item.getElementsByTagName('viewItemURL')[0].firstChild.nodeValue
                                # only record ebay listings if our model confirms they're a true match to the parsed description 
                                # in the tweet
                                match = checkMatch([ebayName, itemdescr])
                                if match:
                                    ins = insert(match_table).values(
                                                tweet_id = tid,
                                                merchant = 'ebay',
                                                merchant_description = ebayName,
                                                merchant_price = ebayPrice,
                                                url = ebayURL
                                                )   
                                    result = connection.execute(ins)
                                    print "matching ebay listing successfully recorded with id:"
                                    print result.inserted_primary_key 
                        except:
                            print "could not process listing"
                            pass
                except:
                    print "could not query ebay for matches to " + itemdescr
                    pass               
        
if __name__ == '__main__':
    main()

