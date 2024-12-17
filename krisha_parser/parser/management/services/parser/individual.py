from requests import Session

from .base import get_page_soup


def get_apartment_info(_id: str, session: Session) -> dict:
    link = f"https://m.krisha.kz/a/show/{_id}"
    soup = get_page_soup(link, session)
    res = session.get(f"https://m.krisha.kz/analytics/aPriceAnalysis/?id={_id}").json()

    ap_data = {
        "link": link,
    }

    for info in soup.findAll('div', class_='attributes__item'):
        label = info.findChildren("span", class_="attributes__item-label", recursive=False)[0].text.strip()
        val = info.findChildren("span", class_="attributes__item-value", recursive=False)[0].text.strip()
        if label == "Этаж" and len(val.split()) == 3:
            ap_data["floor"] = val.split()[0]
            ap_data["max_floor"] = val.split()[2]
        else:
            ap_data[label] = val

    # residential
    residence = soup.findAll('div', class_='a-show-complex-info__text')
    ap_data["residential_complex"] = " - ".join(
        map(
            lambda x: x.strip(),
            filter(
                lambda x: x.replace(" ", ""),
                residence[0].text.strip().split("\n")
            )
        )
    ) if residence else None
    # desc
    ap_data["description"] = res["advert"]["description"]
    ap_data["full_address"] = res["advert"]["fullAddress"]

    # date
    ap_data["post_date"] = res["advert"]["addedAt"]
    ap_data["created_at"] = res["advert"]["createdAt"]
    ap_data["price"] = res["currentPrice"]
    return ap_data
