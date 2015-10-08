from datetime import datetime
import pysentiment as ps
import pandas as pd
import re

date_splitter = re.compile(' [-+]')
hiv4 = ps.HIV4()

def clean_date(date_string):
    cleaned_datestring = date_splitter.split(date_string)[0]
    date_obj = datetime.strptime(cleaned_datestring,'%a, %d %b %Y %H:%M:%S')
    rtn_date = date_obj.strftime("%m/%d/%Y")
    return rtn_date

def get_sentiment(txt):
    tokens = hiv4.tokenize(txt)
    score = hiv4.get_score(tokens)
    return score

def get_subscore(sent_dict, col):
    return sent_dict[col]


emails = pd.read_csv("extracted_emails.csv")
emails = emails.loc[list(map(lambda x : 'nan' not in str(x[0]) and type(x[1]) == str, zip(emails.dates, emails.texts)))]
date = emails.dates.map(clean_date)
sentiment = emails.texts.map(get_sentiment)
polarity = list(map(lambda x : get_subscore(x, 'Polarity'), sentiment)) 
positive = list(map(lambda x : get_subscore(x, 'Positive'), sentiment)) 
negative = list(map(lambda x : get_subscore(x, 'Negative'), sentiment)) 
subjectivity = list(map(lambda x : get_subscore(x, 'Subjectivity'), sentiment))
recipient = emails.recips
sent_frame = pd.DataFrame({'date': date, 'recipient': recipient, 'polarity': polarity, 'positive': positive
    , 'negative': negative, 'subjectivity': subjectivity})
sent_frame.to_csv("email_sentiment.csv")