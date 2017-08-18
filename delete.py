from pymongo import MongoClient


def delete_one(user, list_id):

    # connect to DB (MongoDB)
    client = MongoClient("MONGODB_CO_STRING")
    db = client.lbc

    # update an instance given its list_id and user_id so that the user won't see it any longer
    db.phone.update_one({"user": user, "list_id": list_id}, {"$set": {"user": ""}}, upsert=False)

    return


def delete_all(user):

    # connect to DB (MongoDB)
    client = MongoClient("MONGODB_CO_STRING")
    db = client.lbc

    # delete all instances given its user_id so that the user won't see it any longer
    db.phone.update_many({"user": user}, {"$set": {"user": ""}}, upsert=False)

    return
