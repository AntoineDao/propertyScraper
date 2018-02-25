from propertyscraper.search import RentedSearch
import json
from pymongo import MongoClient
import time
import datetime

config = open("config.json").read()
config = json.loads(config)

# Search Parameters
zoopla_link = config["search"]["zoopla"]
rightmove_link = config["search"]["rightmove"]
gumtree_link = config["search"]["gumtree"]

# MongoDB parameters
user = config["mongo"]["user"]
pword = config["mongo"]["pword"]
connect_address = config["mongo"]["address"]
Database = config["mongo"]["database"]
Collection =config["mongo"]["collection"]

connect_url = "mongodb://{}:{}@{}".format(user, pword, connect_address)
print(connect_url)
client = MongoClient(connect_url)
db = client[Database]
collection = db[Collection]

def results_to_mongo(results, collection, timestamp, source):
    for item in results.data:
        if collection.find_one({"href": item.href}):
            pass
        else:
            collection.insert_one({"result": item.to_json(), "timestamp":timestamp, "retrieved_from": source} )

zoopla_search = RentedSearch.from_zoopla(zoopla_link)
rightmove_search = RentedSearch.from_rightmove(rightmove_link)
gumtree_search = RentedSearch.from_gumtree(gumtree_link)

timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')

results_to_mongo(zoopla_search, collection, timestamp, "zoopla")
results_to_mongo(rightmove_search, collection, timestamp, "rightmove")
results_to_mongo(gumtree_search, collection, timestamp, "gumtree")

            
