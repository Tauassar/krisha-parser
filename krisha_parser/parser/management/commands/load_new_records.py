import sys
import signal
import warnings
from typing import Iterator

from django.core.management import BaseCommand

from krisha_parser.parser.enum import RecordState
from krisha_parser.parser.management.loader import AbstractSplitLoader

from krisha_parser.parser.models import Record

from krisha_parser.parser.management.services.parser.base import get_page_soup, get_max_page, get_ids_from_page
from krisha_parser.parser.management.services.parser.individual import get_apartment_info
from krisha_parser.parser.management.services.session import s


def get_krisha_id_by_link_generator(_link: str):
    def krisha_id_generator():
        soup = get_page_soup(_link, s)
        max_page = get_max_page(soup)

        for page in range(1, max_page+1):
            if page == 1:
                ids = get_ids_from_page(soup)
            else:
                ids = get_ids_from_page(get_page_soup(_link + f"&page={page}", s))

            for _id in ids:
                # sys.stdout.write(f"processing {_id}\n")
                if not Record.objects.filter(kid=_id).exists():
                    yield _id
                else:
                    ...
                    # sys.stdout.write(f"skipping {_id}, since record for this id already exists\n")

            sys.stdout.write(f"finished processing data from {page = }.\n")

    return krisha_id_generator


class KrishaReadingMixin:
    _LINK: str = "https://krisha.kz/prodazha/kvartiry/astana-esilskij/?areas=p51.138213%2C71.403278%2C51.153564%2C71.406655%2C51.144648%2C71.430305%2C51.127191%2C71.443639%2C51.113577%2C71.450473%2C51.106631%2C71.458222%2C51.105283%2C71.465751%2C51.102515%2C71.469268%2C51.090987%2C71.458482%2C51.084655%2C71.448555%2C51.078044%2C71.437967%2C51.069757%2C71.424403%2C51.071670%2C71.412643%2C51.081909%2C71.396591%2C51.095869%2C71.386289%2C51.105032%2C71.389655%2C51.128187%2C71.395769%2C51.130213%2C71.380393%2C51.140712%2C71.384337%2C51.138213%2C71.403278&das[_sys.hasphoto]=1&das[flat.floor][from]=3&das[floor_not_first]=1&das[floor_not_last]=1&das[house.year][from]=2017&das[live.rooms][]=2&das[live.rooms][]=3&das[live.square][from]=57&das[price][to]=40000000&lat=51.08502&lon=71.41745&zoom=14"

    def get_reader(self) -> tuple[list[str], Iterator[list[str]]]:
        return ["kid"], get_krisha_id_by_link_generator(self._LINK)()


class KrishaSplitLoader(KrishaReadingMixin, AbstractSplitLoader):
    MODEL = Record
    FILE_PATH = None
    POOL_LIMIT = 0

    def create_object(self, data):
        info = get_apartment_info(data, s)
        return self.MODEL(
            state=RecordState.PENDING,
            kid=data,
            data=info,
            price=info["price"],
        )


class Command(BaseCommand):
    loader = None

    def handle(self, *args, **options):
        warnings.filterwarnings("ignore")

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.loader = KrishaSplitLoader()
        self.loader.load()

    def shutdown(self, signum, frame):
        if self.loader:
            self.loader.stop()
