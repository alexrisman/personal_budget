from bestbuy import *
from credentials import *

bb = BestbuyClient(api_key)
bb.products_fields = ['sku', 'name','regularPrice', 'salePrice', 'manufacturer','shortDescription']
bb.categories_fields = ['name']
products = bb.products(query='longDescription =iPhone*')
for product in products:
    print product