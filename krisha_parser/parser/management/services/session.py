from requests import Session, adapters
from urllib3.util import retry

s = Session()
# s.proxies.update({
#     "http": "http://BR1NKN5IETWH0TJKL7Q11UEFWJQAN2QB8I07F43ABQBHJ7HD9U9NMFF54GGAETTZ29SARIJQ9NGBOUM7:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8886",
#     "https": "https://BR1NKN5IETWH0TJKL7Q11UEFWJQAN2QB8I07F43ABQBHJ7HD9U9NMFF54GGAETTZ29SARIJQ9NGBOUM7:render_js=False&premium_proxy=True@proxy.scrapingbee.com:8887"
# })
# s.verify = False

_ADAPTER = adapters.HTTPAdapter(
    max_retries=retry.Retry(total=5, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
)  # type: ignore
# apply retries
s.mount("https://", _ADAPTER)
s.mount("http://", _ADAPTER)
