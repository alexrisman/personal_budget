import ebaysdk
from ebaysdk.finding import Connection as finding

f = finding()
f.execute('findItemsAdvanced', {'keywords': 'iPhone'})

dom    = f.response_dom()
mydict = f.response_dict()
myobj  = f.response_obj()

print myobj.itemSearchURL

# process the response via DOM
items = dom.getElementsByTagName('item')

for item in items:
    print item.getElementsByTagName('title')[0].firstChild.nodeValue