from pymongo import MongoClient
from bson.json_util import dumps


def return_ad_one(list_id, user):

    # connect to DB (MongoDB)
    client = MongoClient("MONGODB_CO_STRING")
    db = client.lbc

    # return an instance given its list_id
    ad = db.phone.find_one({"list_id": list_id, "user": user})

    if user == "":
        return

    elif user == "XXXXXXXXXX":

        return dumps(db.phone.find({"list_id": list_id}))

    else:
        return dumps(ad)


def return_ad_all(user):

    # connect to DB (MongoDB)
    client = MongoClient("MONGODB_CO_STRING")
    db = client.lbc

    # return all instances given a user_id
    ads = db.phone.find({"user": user})

    if user == "":
        return

    elif user == "XXXXXXXXXX":

        return dumps(db.phone.find({}))

    else:
        return dumps(ads)
