# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, Response
import json
from delete import delete_one, delete_all
from return_results import return_ad_one, return_ad_all
from flask_basicauth import BasicAuth
from rq import Queue
from worker import conn
from get_phone import get_phone


app = Flask(__name__)


app.config["BASIC_AUTH_USERNAME"] = "XXXXXXXXXX"
app.config["BASIC_AUTH_PASSWORD"] = "XXXXXXXXXX"
app.config["BASIC_AUTH_FORCE"] = True


basic_auth = BasicAuth(app)


@app.route("/secret")
@basic_auth.required
def secret_view():
    return jsonify({"status": "Don't mess with our API!"})


@app.route("/phone", methods=["POST"])
def phone():
    data = request.data
    data_dict = json.loads(data)
    url = data_dict["url"]
    user = data_dict["user"]

    q = Queue(connection=conn)
    q.enqueue(get_phone, args=[url, user], timeout=1200)

    return jsonify({"status": "success"})


@app.route("/delete_one_ad", methods=["POST"])
def delete_one_ad():
    data = request.data
    data_dict = json.loads(data)
    list_id = data_dict["list_id"]
    user = data_dict["user"]
    delete_one(user=user, list_id=list_id)

    return jsonify({"status": "success"})


@app.route("/delete_all_ads", methods=["POST"])
def delete_all_ads():
    data = request.data
    data_dict = json.loads(data)
    user = data_dict["user"]
    delete_all(user=user)

    return jsonify({"status": "success"})


@app.route("/ad", methods=["GET"])
def ad():
    list_id = request.args.get("list_id")
    user = request.args.get("user")

    data = app.response_class(response=return_ad_one(list_id=list_id, user=user), status=200, mimetype="application/json")

    return data


@app.route("/ad_all", methods=["GET"])
def ad_all():
    user = request.args.get("user")

    data = app.response_class(response=return_ad_all(user=user), status=200, mimetype="application/json")

    return data


@app.route("/send_sms", methods=["POST"])
def send_sms():
    data = request.data
    data_dict = json.loads(data)
    user = data_dict["user"]
    list_id = data_dict["list_id"]

    return jsonify({"status": "success"})
