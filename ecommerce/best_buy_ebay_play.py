from bestbuy import *
from credentials import *
from ebaysdk.finding import Connection as finding
import ebaysdk
import numpy as np
import pandas as pd
import multiprocessing

bb = BestbuyClient(api_key)

# columns for price table
upcs_for_price_frame = []
ebay_prices = []
best_buy_prices = []

# columns for match table
ebay_names_for_match_frame = []
best_buy_names_for_match_frame = []
match_inds = []

# columns for best buy table
upcs_for_best_buy_frame = []
names_for_best_buy_frame = []

# columns for ebay table
upcs_for_ebay_frame = []
names_for_ebay_frame = []
ids_for_ebay_frame = []


bb.products_fields = ['upc', 'name','regularPrice']

def processPage(pageNbr):
	try:
		products = bb.products(page = pageNbr)
		for product in products:
			best_buy_name = product['name']
			product_upc  = product['upc']
			best_buy_price = product['regularPrice']
			f = finding()
			f.execute('findItemsByProduct', '<productId type="UPC">' + product_upc + '</productId>')
			dom = f.response_dom()
			items = dom.getElementsByTagName('item')
			if len(items) > 0:
				try:
					ebay_names = list(map(lambda x : x.getElementsByTagName('title')[0].firstChild.nodeValue, items))
					first_item = items[0]
					ebay_id = first_item.getElementsByTagName('productId')[0].firstChild.nodeValue
					ebay_price = first_item.getElementsByTagName('sellingStatus')[0].getElementsByTagName('currentPrice')[0].firstChild.nodeValue

					# add to price table
					upcs_for_price_frame.append(product_upc)
					ebay_prices.append(ebay_price)
					best_buy_prices.append(best_buy_price)

					# add to best buy table
					upcs_for_best_buy_frame.append(product_upc)
					names_for_best_buy_frame.append(best_buy_name)

					# add to ebay table
					for ebay_name in ebay_names:
						upcs_for_ebay_frame.append(product_upc)
						names_for_ebay_frame.append(ebay_name)
						ids_for_ebay_frame.append(ebay_id)
						# add to match table
						ebay_names_for_match_frame.append(ebay_name)
						best_buy_names_for_match_frame.append(best_buy_name)
						match_inds.append(1)
					f = finding()
					f.execute('findItemsAdvanced', {'keywords': best_buy_name})
					dom = f.response_dom()
					items = dom.getElementsByTagName('item')[:10]
					if len(items) > 0:
						for item in items:
							curr_ebay_id = item.getElementsByTagName('productId')[0].firstChild.nodeValue
							if curr_ebay_id != ebay_id:
								curr_ebay_name = item.getElementsByTagName('title')[0].firstChild.nodeValue
								best_buy_names_for_match_frame.append(best_buy_name)
								ebay_names_for_match_frame.append(curr_ebay_name)
								match_inds.append(0)
				except:
					pass
	except:
		pass

pool = multiprocessing.Pool(4)
# pool.map(processPage, np.arange(1,5))
for i in np.arange(1,50):
	processPage(i)

price_frame = pd.DataFrame({'UPC': upcs_for_price_frame, 'best_buy_price': best_buy_prices
	, 'ebay_price': ebay_prices})
ebay_frame = pd.DataFrame({'UPC': upcs_for_ebay_frame, 'product_id': ids_for_ebay_frame
	, 'name': names_for_ebay_frame})
best_buy_frame = pd.DataFrame({'UPC': upcs_for_best_buy_frame, 'name': names_for_best_buy_frame})
match_frame = pd.DataFrame({'best_buy_name': best_buy_names_for_match_frame
	, 'ebay_name': ebay_names_for_match_frame, 'match_ind': match_inds})

price_frame.to_csv('ebay_best_buy_data/price_table.csv', index=False, encoding='utf-8')
ebay_frame.to_csv('ebay_best_buy_data/ebay_table.csv', index=False, encoding='utf-8')
best_buy_frame.to_csv('ebay_best_buy_data/best_buy_table.csv', index=False, encoding='utf-8')
match_frame.to_csv('ebay_best_buy_data/match_table.csv', index=False, encoding='utf-8')





