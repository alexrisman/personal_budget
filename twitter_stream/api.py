__author__ = 'matt'

from flask import Flask
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.runner import Runner
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.sql.expression import func

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

class OutputTable(object):
    pass

class Tweets(Resource):

    def loadSession(self):

        dbPath = 'tweet_output.db'
        engine = create_engine('sqlite:///%s' % dbPath, echo=True)

        metadata = MetaData(engine)
        output = Table('output', metadata, autoload=True)
        clear_mappers()
        mapper(OutputTable, output)

        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def get(self, min_rqst, max_rqst):
        session = self.loadSession()
        cntres = session.query(func.max(OutputTable.output_id))
        num_deals = cntres[0][0]
        min_rqst = max(min_rqst,0)
        max_rqst = max(min_rqst, max_rqst)
        min_slct = num_deals-max_rqst
        max_slct = num_deals-min_rqst
        res = session.query(OutputTable).all()
        deal_list = []
        for i in range(max_slct*(-1), min_slct*(-1)):
            j=i*(-1)-1
            try:
                deal_list.append({
                'tweet_ts': res[j].tweet_ts,
                'tweet_text': res[j].orig_text,
                'desc': res[j].description,
                'price': res[j].price,
                'url': res[j].url,
                'best_price': res[j].best_price,
                'best_link': res[j].best_url
                })
            except:
                pass
            
        return [num_deals, deal_list]

# API ROUTING
api.add_resource(Tweets, '/tweets/<int:min_rqst>&<int:max_rqst>')

if __name__ == "__main__":
    runner.run()
