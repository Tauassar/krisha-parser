import random
import signal
import sys
import warnings
from time import sleep

import tenacity
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.db import OperationalError, close_old_connections, connection, connections

from krisha_parser.parser.enum import RecordState

from krisha_parser.parser.models import Record

from krisha_parser.parser.management.services.session import s


class Command(BaseCommand):
    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(OperationalError),
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
    )
    def expire(self, inst: Record):
        try:
            sys.stdout.write(f"{Record.objects.filter(kid=inst.kid) = } {inst.kid = } expired, deleting it.\n")
            Record.objects.filter(kid=inst.kid).update(
                expired=True,
                state=RecordState.REJECTED
            )
        except OperationalError:
            connections.close_all()
            sys.stdout.write(f"{inst.kid = } retry.\n")
            raise

    def handle(self, *args, **options):
        warnings.filterwarnings("ignore")

        counter = 0

        for inst in Record.objects.filter(state=RecordState.APPROVED):
            res = s.get(inst.plain_link)
            soup = BeautifulSoup(res.text, "html.parser")

            if (
                res.status_code >= 400
                or len(
                    soup.findAll(
                        'span',
                        class_='paid-labels__item paid-labels__item--red',
                    )
                )
            ):
                counter += 1
                self.expire(inst)
            else:
                sys.stdout.write(f"{inst.kid = } passed check.\n")

            sleep(random.uniform(0.4, 2))
        sys.stdout.write(f"finished checking instances for expiration.\n")
