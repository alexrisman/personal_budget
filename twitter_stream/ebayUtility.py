from ebaysdk.finding import Connection as finding
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import pdist
import string

dist_metrics = ['euclidean', 'cityblock', 'chebyshev', 'hamming', 'cosine']
exclude = set(string.punctuation)
print "loading matching model"
with open("matchModel.pickle", 'rb') as f:
    clf = pickle.load(f)
print "finished loading matching model"

# perform keyword search through eBay API
def getEbayItems(searchArgument):
    f = finding()
    f.execute('findItemsAdvanced', {'keywords': searchArgument})
    dom = f.response_dom()
    items = dom.getElementsByTagName('item')[:20]  
    return items  

# derive features for matching model from string pairs
def dists(s1, s2):
    returnDists = [-1,-1,-1,-1,-1]
    try:
        vecs = CountVectorizer().fit_transform([s1,s2]).todense()
        dists = list(map(lambda x : pdist(vecs, x)[0], dist_metrics))
        returnDists = []
        for dist in dists:
            if np.isnan(dist):
                returnDists.append(-1)
            else:
                returnDists.append(dist)
    except:
        pass
    return returnDists

def xWordSame(s1, s2, ind):
    return s1.split()[ind]==s2.split()[ind]

def lenInWords(s):
    return len(s.split())

def differentNumber(s1, s2, date_ind):
    rtn_ind = False
    s1 = ''.join(ch for ch in s1 if ch not in exclude)
    s2 = ''.join(ch for ch in s2 if ch not in exclude)
    if date_ind:
        s1_numbers = set(list(filter(lambda x : len(str(x))==4,[int(s) for s in s1.split() if s.isdigit()])))
        s2_numbers = set(list(filter(lambda x : len(str(x))==4,[int(s) for s in s2.split() if s.isdigit()])))
    else:
        s1_numbers = set([int(s) for s in s1.split() if s.isdigit()])
        s2_numbers = set([int(s) for s in s2.split() if s.isdigit()])
    number_intersection = s1_numbers.intersection(s2_numbers)
    if len(s1_numbers) != len(number_intersection):
        rtn_ind = True
    return rtn_ind  

def getFeatures(sPair):
    rtnFeatures = []
    s1 = sPair[0]
    s2 = sPair[1]
    currDists = dists(s1,s2)
    lastWordSame = xWordSame(s1,s2,-1)
    firstWordSame = xWordSame(s1,s2,0)
    s1Len = lenInWords(s1)
    s2Len = lenInWords(s2)
    diffNum = differentNumber(s1,s2,False)
    diffDate = differentNumber(s1,s2,True)
    for dist in currDists:
        rtnFeatures.append(dist)
    rtnFeatures.append(lastWordSame)
    rtnFeatures.append(firstWordSame)
    rtnFeatures.append(s1Len)
    rtnFeatures.append(s2Len)
    rtnFeatures.append(diffNum)
    rtnFeatures.append(diffDate)
    return rtnFeatures

def checkMatch(sPair):
	rtnInd = False
	features = np.array([getFeatures(sPair)])
	matchInd = clf.predict(features)[0]
	if matchInd == 1:
		rtnInd = True
	return rtnInd

