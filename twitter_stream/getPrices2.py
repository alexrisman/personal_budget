#! /usr/bin/env python27
# -*- coding: latin-1 -*-
import nltk
import re

grammar = r"""
PRICE: {<\$><CD.*>+}
NP: {<DT|JJ|CD|VBG|NNP.*>+}
"""
tp = nltk.RegexpParser(grammar)

pattern = r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'

from pymongo import MongoClient
client = MongoClient()

db = client.dealtrader
collection = db.raw_tweets

tweets = collection.count()

for index in range(4035, tweets): 
    tweet = collection.find()[index]
    urls = re.findall(pattern, tweet['text'])
    remainder = re.sub(pattern, '', tweet['text'])
    tree = tp.parse(nltk.pos_tag(nltk.word_tokenize(remainder)))
    for obj in nltk.tree.Tree.subtrees(tree):
        if obj.label() == 'PRICE':
            print "URL: {0}\t{1}".format(urls[0][0],obj.flatten())
