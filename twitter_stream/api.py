__author__ = 'matt'

from flask import Flask
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.runner import Runner
import datetime
import time
import numpy as np
import json
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.sql.expression import func
#from copy import deepcopy
#from ast import literal_eval

app = Flask(__name__)
runner = Runner(app)
api = Api(app)

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def get_key(item):
    return item.values()[0]

class Deals(object):
    pass

class Tweets(Resource):

    def loadSession(self):

        dbPath = 'tweet.db'
        engine = create_engine('sqlite:///%s' % dbPath, echo=True)

        metadata = MetaData(engine)
        deals = Table('deals', metadata, autoload=True)
        clear_mappers()
        mapper(Deals, deals)

        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def get(self, num_rqst):
        session = self.loadSession()
        cntres = session.query(func.max(Deals.deal_id))
        num_deals = cntres[0][0]
        min_deal = max(num_deals-num_rqst,0)
        deal_range = {'min': min_deal, 'max': num_deals}
        res = session.query(Deals).all()
        deal_list = []
        for i in range(min_deal, num_deals):
            deal_list.append({
                'tweet_id': res[i].tweet_id,
                'description': res[i].description,
                'price': res[i].price,
                'url': res[i].url
            })
        return deal_list

# API ROUTING
api.add_resource(Tweets, '/tweets/<int:num_rqst>')

if __name__ == "__main__":
    runner.run()