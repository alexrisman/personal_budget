__author__ = 'matt'

from sqlalchemy import MetaData, Table, Column, Integer, Numeric, String, DateTime, ForeignKey, create_engine, BigInteger, insert
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.sql.expression import func
from pymongo import MongoClient
import ast
from bson.json_util import dumps

# Create a SQLite db using sqlalchemy
def init_db():
    # create a new metadata object
    metadata = MetaData()
    # build our tweets table
    output = Table('output', metadata,
              Column('output_id', Integer(), primary_key=True),
              Column('deal_id', Integer()),
              Column('tweet_id', BigInteger()),
              Column('orig_text', String(255)),
              Column('tweet_ts', String(255)),
              Column('description', String(255)),
              Column('price', String(15)),
              Column('url', String(255)),
              Column('best_price', String(15)),
              Column('best_url', String(255))
               )
    # now make a new file based SQLite3 db
    engine = create_engine('sqlite:///tweet_output.db')
    # and build it
    metadata.create_all(engine)
    # return the handle so we can talk to it
    return engine, output

class Deals(object):
    pass

class Matches(object):
    pass

def loadTables():

        dbPath = 'tweet.db'
        engine = create_engine('sqlite:///%s' % dbPath, echo=True)

        metadata = MetaData(engine)
        deals = Table('deals', metadata, autoload=True)
        matches = Table('price_check_history', metadata, autoload=True)
        mapper(Deals, deals)
        mapper(Matches, matches)

        Session = sessionmaker(bind=engine)
        session = Session()
        return session

class Output(object):
    pass

def loadOutput():

        dbPath = 'tweet_output.db'
        engine = create_engine('sqlite:///%s' % dbPath, echo=True)

        metadata = MetaData(engine)
        output = Table('output', metadata, autoload=True)
        mapper(Output, output)

        Session = sessionmaker(bind=engine)
        session = Session()
        return session

def main():
    # First create the SQL db that we will dump to
    engine, table = init_db()
    connection = engine.connect()

    # Load up all this stuff - crappy code but it works (clean up if time but this whole script is a shoddy hack)
    clear_mappers()
    session = loadTables()
    session2 = loadOutput()

    # create a connection to the mongo DB
    client = MongoClient()
    db = client.dealtrader
    collection = db.raw_tweets

    while True:
        # get number of deals in the table
        cnttot = session.query(func.max(Deals.deal_id))
        num_deals = cnttot[0][0]
        #print num_deals

        cntdone = session2.query(func.max(Output.deal_id))
        min_deal = cntdone[0][0] or 0
        #print min_deal

        res = session.query(Deals).all()

        for i in range(min_deal, num_deals):
            tweetid = int(res[i].tweet_id)
            q =  session.query(Matches)
            mchres = q.filter(Matches.tweet_id == tweetid).all()
            tweet = collection.find_one( { 'id': tweetid } )
            try:
                deal_id = res[i].deal_id
                origtext = tweet['text']
                tweetts = str(tweet['created_at'])
                itemdescr = res[i].description
                itemprice = res[i].price
                itemurl = res[i].url
                lowest_price = min(list(map(lambda x : x.merchant_price, mchres)))
                best_listings = list(filter(lambda x : x.merchant_price==lowest_price, mchres))
                best_listing = best_listings[0]
                bestprice = str(best_listing.merchant_price)
                bestlink = str(best_listing.url)

                ins = insert(table).values(
                                deal_id = deal_id,
                                tweet_id = tweetid,
                                orig_text = origtext,
                                tweet_ts = tweetts,
                                description = itemdescr,
                                price = itemprice,
                                url = itemurl,
                                best_price = bestprice,
                                best_url = bestlink
                                )
                result = connection.execute(ins)
            except:
                pass

if __name__ == '__main__':
    main()