import logging

import requests
from requests.exceptions import ProxyError

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # print(p)
    i = 0

    while i < 11:
        try:
            res = requests.get(
                "https://api.ipify.org/?format=json",
                timeout=5,
                verify=False,
                proxies={
                    "http": "http://BR1NKN5IETWH0TJKL7Q11UEFWJQAN2QB8I07F43ABQBHJ7HD9U9NMFF54GGAETTZ29SARIJQ9NGBOUM7:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8886",
                    "https": "https://BR1NKN5IETWH0TJKL7Q11UEFWJQAN2QB8I07F43ABQBHJ7HD9U9NMFF54GGAETTZ29SARIJQ9NGBOUM7:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8887"
                }
            )
        except (ProxyError, TimeoutError):
            print("Proxy error occured")
            continue

        print(res.text)
        i += 1
