import csv
import queue
import sys
import threading
import typing

from django.core.cache import cache
from django.db import models


STOP = threading.Event()


class Filler(threading.Thread):
    def __init__(
        self,
        queue_: queue.Queue,
        headers: list[str],
        reader: typing.Iterator[list[str]],
        creator: typing.Callable[[list], typing.Any],
        limit: int,
    ):
        super().__init__()
        self._queue = queue_
        self._headers = headers
        self._reader = reader
        self._creator = creator
        self._limit = limit

    def run(self) -> None:
        objects_pool = []
        sys.stdout.write(
            f'Headers are {self._headers}\n',
        )

        row_index = 0
        pool_size = 0

        while True:
            if STOP.is_set():
                break

            try:
                data_row = next(self._reader)
            except StopIteration:
                STOP.set()
                break

            created_object = self._creator(data_row)

            if hasattr(data_row, "clear"):
                data_row.clear()

            if created_object is not None:
                objects_pool.append(created_object)
                pool_size += 1

            if pool_size > self._limit:
                self._queue.put(
                    objects_pool.copy(),
                )
                sys.stdout.write(
                    f'{pool_size} objects put to queue for creation '
                    f'and pools in queue is {self._queue.qsize()}\n',
                )
                objects_pool.clear()
                pool_size = 0

            row_index += 1


class Creator(threading.Thread):
    def __init__(
        self,
        queue_: queue.Queue,
        model: models.Model,
        num: int = 1,
    ):
        super().__init__()
        self._queue = queue_
        self._model = model
        self._num = num

    def run(self) -> None:
        created = 0

        while True:
            if STOP.is_set() and self._queue.empty():
                break
            try:
                pool = self._queue.get(timeout=1)
            except queue.Empty:
                continue
            if pool is STOP:
                break

            pool_size = len(pool)
            self._model.objects.bulk_create(
                pool,
                batch_size=50000,
                ignore_conflicts = True,
            )
            pool.clear()
            created += pool_size
            print(
                f'Worker-{self._num} {len(pool)} objects created, '
                f'all created objects num is {created}',
            )
            self._queue.task_done()
        print(f'Finished with all created objects num {created}')


class AbstractSplitLoader:
    MODEL = None
    FILE_PATH = ''
    POOL_LIMIT = 2000
    QUEUE_SIZE = 5
    CREATOR_NUM = 1
    _file = None
    _threads = []

    def get_reader(self) -> tuple[list[str], typing.Iterator[list[str]]]:
        self._file = open(self.FILE_PATH)
        csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
        data_reader = csv.reader(self._file, dialect='piper')
        headers = next(data_reader)
        return headers, data_reader

    def load(self):
        headers, reader = self.get_reader()

        queue_ = queue.Queue(maxsize=self.QUEUE_SIZE)

        # self._threads.append()
        self._threads = [
            Filler(
                queue_,
                headers,
                reader,
                self.create_object,
                self.POOL_LIMIT,
            )
        ]
        self._threads += [
            Creator(queue_, self.MODEL, i + 1)
            for i in range(self.CREATOR_NUM)
        ]
        for thread in self._threads:
            thread.start()

        for thread in self._threads:
            thread.join()

    def create_object(self, data):
        raise NotImplementedError

    def stop(self):
        STOP.set()


class AbstractLoader:

    MODEL = None
    FILE_PATH = ''
    POOL_LIMIT = 2000
    SERIALIZER = None
    SKIP_ROW = False

    @classmethod
    def load(cls):
        objects_pool = []
        row_index = 0
        # model_attributes = list([field.name for field in cls.MODEL._meta.fields])
        csv.field_size_limit(100000000)
        data_rows = cls.get_rows()
        sys.stdout.write(f'Colum name is {next(data_rows)}')
        load_pointer = cache.get('load_pointer')
        bulk_result = 0
        for data_row in data_rows:
            if cls.SKIP_ROW and load_pointer is not None:
                if row_index < load_pointer:
                    row_index += 1
                    continue
            created_object = cls.create_object(data_row)
            if created_object is not None:
                objects_pool.append(created_object)

            if len(objects_pool) > cls.POOL_LIMIT:
                bulk_result += len(cls.MODEL.objects.bulk_create(objects_pool, ignore_conflicts=True))
                objects_pool.clear()
            row_index += 1

            cache.set('load_pointer', row_index)

        if len(objects_pool) > 0:
            bulk_result += len(cls.MODEL.objects.bulk_create(objects_pool, ignore_conflicts=True))

        sys.stdout.write(f"{bulk_result} objects created during bulk-creation\r")

    @classmethod
    def create_object(cls, data):
        """
            This function creates the object. Pay attention to word CREATE! not save but CREATE!
            It does not hit the database, but just CREATE!s the object instance in order to use
            pool of CREATE!d objects to perform bulk-CREATE! operation, that saves you bunch of time.
            Good Luck!

        :param row:
        :return: CREATED! object
        """
        raise NotImplementedError

    @classmethod
    def normalize_row(cls, row):
        """
            This function is a kernel of our class. It helps to extract only required data
            from unstructured row and use the output of current method to create objects in
            in serializers.
            Good Luck!

        :param row:
        :return: normalized row
        """
        return row

    @classmethod
    def get_rows(cls):
        """
            This function is generator for getting csv rows.
            Good Luck!

        :param :
        :yields : rows from csv
        """
        with open(cls.FILE_PATH) as csv_file:
            csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
            data_reader = csv.reader(csv_file, dialect='piper')
            yield next(data_reader)
            for row in data_reader:
                yield [str(column) for column in row]
