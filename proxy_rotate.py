import requests


def get_proxy():

    # API used : https://www.proxicity.io/api
    # Check for API rate limit

    url = "https://api.proxicity.io/v2/XXXXXXXXXXX/proxy?protocol=http&country=FR&httpsSupport=true"

    response = requests.request("GET", url)

    ip = response.json()["ipAddress"]
    port = response.json()["port"]

    data = {'http': str('http' + "://" + str(ip) + ":" + str(port)),
            'https': str('https' + "://" + str(ip) + ":" + str(port))}

    return data
