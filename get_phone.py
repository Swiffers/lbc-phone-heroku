# -*- coding: utf-8 -*-

import requests
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
from random_uagents import random_ua
from proxy_rotate import get_proxy
from requests.exceptions import ProxyError, SSLError, ConnectionError


def get_phone(search_url, user_id):

    # set the list of profile url we want to parse
    profile_urls = []

    # connect to DB (MongoDB)
    client = MongoClient("MONGODB_CO_STRING")
    db = client.lbc

    # get the search url by asking user
    if "https://www.leboncoin.fr/" not in search_url:
        raise Exception("Votre URL n'est pas valide, vérifiez qu'elle ait bien le format suivant : https://www.leboncoin.fr/annonces/...")
    else:
        pass

    # get all the ads' urls
    headers1 = {"cache-control": "no-cache"}
    html_home1 = requests.request("GET", str(search_url), headers=headers1).text
    soup1 = BeautifulSoup(html_home1, "html.parser")

    soup2 = soup1("a")
    soup3 = BeautifulSoup(str(soup2), "html.parser")

    for aclass in soup3:
        try:
            raw_url = aclass.get("href")
            profile_urls.append("https:" + raw_url)
        except (TypeError, AttributeError):
            pass

    # get the phone number, title, ad id and category if available and save the result to a Mongo Collection
    for profile_url in profile_urls:

        if db.phone.find_one({"url": profile_url}) is None:

            try:
                proxy = get_proxy()
                string_list_id = profile_url.replace("https://www.leboncoin.fr/", "").split("/")
                category = string_list_id[0]
                list_id = (string_list_id[1].split(".htm"))[0]

                phone_url = "https://api.leboncoin.fr/api/utils/phonenumber.json"
                phone_payload = "list_id=" + str(list_id) + "&app_id=leboncoin_web_utils&key=54bb0281238b45a03f0ee695f73e704f&text=1"
                phone_headers = {
                    'accept': "*/*",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "fr,en-US;q=0.8,en;q=0.6,es;q=0.4",
                    'connection': "keep-alive",
                    'content-length': "89",
                    'content-type': "application/x-www-form-urlencoded",
                    'host': "api.leboncoin.fr",
                    'origin': "https://www.leboncoin.fr",
                    'referer': str(profile_url),
                    'user-agent': random_ua(),
                    'cache-control': "no-cache",
                }

                phone = requests.request("POST", phone_url, data=phone_payload, headers=phone_headers, proxies=proxy).json()["utils"]["phonenumber"]
                html_profile = BeautifulSoup(requests.request("POST", str(profile_url), headers=headers1, proxies=proxy).text, "html.parser")
                ad_title = html_profile.find(class_="adview_header clearfix").find("h1").text.lstrip().rstrip()
                name = html_profile.find(class_="uppercase bold trackable").text.lstrip().rstrip()

                # We save results to a Mongo Collection using insert
                data = {"ref_url": search_url, "url": profile_url, "title": ad_title, "category": category, "list_id": list_id, "name": name, "phone": phone, "user": user_id, "created_date": datetime.datetime.utcnow()}
                db.phone.insert_one(data)

                # We add a pause to the loop to avoid being blacklisted by lbc's servers
                # time.sleep(10)

            # if ProxyError is raised we try again to connect using a different proxy
            except (ProxyError, SSLError, ConnectionError):
                try:
                    proxy = get_proxy()
                    string_list_id = profile_url.replace("https://www.leboncoin.fr/", "").split("/")
                    category = string_list_id[0]
                    list_id = (string_list_id[1].split(".htm"))[0]

                    phone_url = "https://api.leboncoin.fr/api/utils/phonenumber.json"
                    phone_payload = "list_id=" + str(
                        list_id) + "&app_id=leboncoin_web_utils&key=54bb0281238b45a03f0ee695f73e704f&text=1"
                    phone_headers = {
                        'accept': "*/*",
                        'accept-encoding': "gzip, deflate, br",
                        'accept-language': "fr,en-US;q=0.8,en;q=0.6,es;q=0.4",
                        'connection': "keep-alive",
                        'content-length': "89",
                        'content-type': "application/x-www-form-urlencoded",
                        'host': "api.leboncoin.fr",
                        'origin': "https://www.leboncoin.fr",
                        'referer': str(profile_url),
                        'user-agent': random_ua(),
                        'cache-control': "no-cache",
                    }

                    phone = requests.request("POST", phone_url, data=phone_payload, headers=phone_headers,
                                             proxies=proxy).json()["utils"]["phonenumber"]
                    html_profile = BeautifulSoup(
                        requests.request("POST", str(profile_url), headers=headers1, proxies=proxy).text, "html.parser")
                    ad_title = html_profile.find(class_="adview_header clearfix").find("h1").text.lstrip().rstrip()
                    name = html_profile.find(class_="uppercase bold trackable").text.lstrip().rstrip()

                    # We save results to a Mongo Collection using insert
                    data = {"ref_url": search_url, "url": profile_url, "title": ad_title, "category": category,
                            "list_id": list_id, "name": name, "phone": phone, "user": user_id,
                            "created_date": datetime.datetime.utcnow()}
                    db.phone.insert_one(data)

                    # We add a pause to the loop to avoid being blacklisted by lbc's servers
                    # time.sleep(10)

                except (ProxyError, SSLError, ConnectionError, AttributeError, IndexError, KeyError):
                    continue

            except (AttributeError, IndexError, KeyError):
                continue

        # We create a new entry in Collection for a new user but without making another request to lbc's API
        elif db.phone.find_one({"url": profile_url, "user": user_id}) is None:

            data2 = db.phone.find_one({"url": profile_url})
            db.phone.insert_one({"url": data2["url"], "title": data2["title"], "category": data2["category"], "list_id": data2["list_id"], "name": data2["name"], "phone": data2["phone"], "user": user_id, "created_date": datetime.datetime.utcnow(), "ref_url": search_url})

        else:
            continue

    # API call to tell our App that the job has been completed
    jd_url = "https://ghapp.bubbleapps.io/api/1.0/wf/job_done" #/version-test/

    jd_headers = {
        'authorization': "Bearer XXXXXXXXXX",
        'content-type': "application/json",
        'cache-control': "no-cache"
    }

    jd_data = "{\n\t\"user_id\":\""+user_id+"\",\n\t\"search_url\":\""+search_url+"\"\n}"

    jd_result = requests.request("POST", jd_url, data=jd_data, headers=jd_headers)

    print(jd_result)

    return
