import sys
from time import sleep

import tenacity
from bs4 import BeautifulSoup
from faker.generator import random
from requests import Session


@tenacity.retry(
    retry=tenacity.retry_if_exception_type(TimeoutError),
    wait=tenacity.wait_chain((3, 5, 15, 60, 300, 1200, 3600)),
    stop=tenacity.stop_after_attempt(5),
)
def get_page_soup(link: str, session: Session) -> BeautifulSoup:
    sys.stdout.write(f"fetching info from the {link = }.\n")
    page = session.get(
        link,
        timeout=4,
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
        },
    )
    page.raise_for_status()
    sleep(random.uniform(0.4, 2))
    return BeautifulSoup(page.text, "html.parser")


def get_max_page(_soup: BeautifulSoup) -> int:
    return max(
        [
            int(getattr(x, "attrs", {}).get("data-page", 0)) for x in _soup.findAll('a', class_='paginator__btn')
        ]
    )


def get_ids_from_page(_soup: BeautifulSoup) -> list[str]:
    cards_list = _soup.findAll('div', class_='a-list__cards')
    if cards_list:
        return [card.attrs["data-id"] for card in cards_list[0].findChildren("div", class_="a-list-item")]
    return []
