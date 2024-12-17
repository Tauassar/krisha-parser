import logging

from .parser.base import get_page_soup, get_max_page, get_ids_from_page
from .parser.individual import get_apartment_info
from .session import s

logging.basicConfig(level=logging.DEBUG)

base_link = "https://krisha.kz/prodazha/kvartiry/astana-esilskij/?areas=p51.140304%2C71.401835%2C51.136225%2C71.446527%2C51.127191%2C71.443639%2C51.113577%2C71.450473%2C51.106631%2C71.458222%2C51.105283%2C71.465751%2C51.102515%2C71.469268%2C51.090068%2C71.460027%2C51.080276%2C71.456537%2C51.075989%2C71.450498%2C51.081909%2C71.396591%2C51.086640%2C71.375088%2C51.105424%2C71.386415%2C51.141522%2C71.399658%2C51.140304%2C71.401835&bounds=&das[_sys.hasphoto]=1&das[flat.floor][from]=3&das[floor_not_first]=1&das[floor_not_last]=1&das[house.year][from]=2010&das[live.rooms][0]=2&das[live.rooms][1]=3&das[live.square][from]=50&das[price][to]=35000000&lat=51.10877&lon=71.42218&zoom=13"


soup = get_page_soup(base_link, s)
max_page = get_max_page(soup)

for page in range(1, max_page+1):
    data = []

    if page == 1:
        ids = get_ids_from_page(soup)
    else:
        ids = get_ids_from_page(get_page_soup(base_link + f"&page={page}", s))

    for _id in ids:
        print(f"processing {_id}")
        data.append(get_apartment_info(_id, s))

    print(f"data from {page = }. {data = }")
