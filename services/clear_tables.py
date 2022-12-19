import pymongo

# ------------- INITIALIZATION --------------------#

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['smallcap_sip_bot']

tri_collection = db['smallcap_bot_totalreturnsindex_data']
user_preferences = db['smallcap_bot_userpreferences']
user_details = db['smallcap_bot_userdetails']
alert_details = db['smallcap_bot_alerts']

# ------------- CLEAR ALL RECORDS --------------------#

tri_collection.delete_many({})
user_preferences.delete_many({})
user_details.delete_many({})
alert_details.delete_many({})