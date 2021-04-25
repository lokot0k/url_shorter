import json

import requests

token = "76cb21db248abe5cbc92ee88a3b9c7669c27b05f"


# через bittly-api сокращаем ссылку и возвращаем ее
def short_link(link):
    header = {"Authorization":
                  f"Bearer {token}"
              }
    url_post = "https://api-ssl.bitly.com/v4/shorten"
    data = {
        "long_url": link
    }
    r = requests.post(url_post, headers=header, data=json.dumps(data))
    try:
        return r.json()["link"]
    except Exception:
        return None
