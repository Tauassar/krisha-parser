import logging
from django.db.models.expressions import RawSQL
from multiprocessing import Process, Lock

import django
from django.contrib import admin, messages

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.core.management import call_command
from import_export.admin import ImportExportModelAdmin

from krisha_parser.common.admin import PrettyJsonMixin
from .enum import RecordState

from .models import Record
from .resources import RecordResource

logger = logging.getLogger(__name__)

LOCK = Lock()


def subprocess_setup():
    django.setup()


def load_run_func(_lock: Lock):
    with _lock:
        subprocess_setup()
        call_command('load_new_records')


def remove_run_func(_lock: Lock):
    with _lock:
        subprocess_setup()
        call_command('remove_expired')


@admin.action(description="Mark selected records as rejected")
def make_reject(modeladmin, request, queryset):
    queryset.update(state=RecordState.REJECTED)


@admin.action(description="Mark selected records as accepted")
def make_accepted(modeladmin, request, queryset):
    queryset.update(state=RecordState.APPROVED)


@admin.action(description="Mark selected records as pending")
def make_pending(modeladmin, request, queryset):
    queryset.update(state=RecordState.PENDING)


@admin.register(Record)
class RecordAdmin(
    ExtraButtonsMixin,
    PrettyJsonMixin,
    ImportExportModelAdmin,
):
    resource_classes = [RecordResource]
    search_fields = ('kid', "data")
    actions = [make_reject, make_accepted, make_pending]
    list_display = (
        'id',
        'kid',
        'state',
        'krisha_link',
        'residential_complex',
        'description',
        'floor',
        'max_floor',
        'total_area',
        'price',
        'total_price',
        'post_date',
        'krisha_created_at',
        'changed_at',
    )
    readonly_fields = (
        'kid',
        'krisha_link',
        'residential_complex',
        'floor',
        'max_floor',
        'post_date',
        'price',
        'krisha_created_at',
        'total_area',
        'description',
        'full_address',
        'data',
    )
    ordering = ('-created_at',)
    list_filter = ('state', "expired")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _area=RawSQL("(data->>'Площадь, м²')::varchar", []),
            _residential_complex=RawSQL("(data->>'residential_complex')::varchar", []),
            _krisha_created_at=RawSQL("(data->>'created_at')::timestamp", []),
            _post_date=RawSQL("(data->>'post_date')::timestamp", []),
        )
        return queryset

    def total_area(self, obj):
        return obj._area
    total_area.admin_order_field = '_area'


    def residential_complex(self, obj):
        return obj._residential_complex
    residential_complex.admin_order_field = '_residential_complex'

    def krisha_created_at(self, obj):
        return obj._krisha_created_at
    krisha_created_at.admin_order_field = '_krisha_created_at'

    def post_date(self, obj):
        return obj._post_date
    post_date.admin_order_field = '_post_date'

    def data(self, obj: Record):
        return self.pretty_raw(obj.data or '')

    @button(
        change_form=True,
        label='Approve'
    )
    def approve(self, request, pk):
        try:
            self.message_user(
                request,
                'Запрос на Approve отправлен в Кред Админ',
            )
        except Exception as e:
            logger.error(str(e))
            self.message_user(
                request,
                f'Неизвестная ошибка при Approve документа: {e}',
                messages.ERROR
            )

    @button(
        change_form=True,
        html_attrs={'style': 'background-color: #eba82d;'},
        label='Reject'
    )
    def reject(self, request, pk):
        try:
            self.message_user(
                request,
                'Запрос на Reject отправлен в Кред Админ',
            )
        except Exception as e:
            logger.error(str(e))
            self.message_user(
                request,
                f'Неизвестная ошибка при Reject документа: {e}',
                messages.ERROR
            )

    @button(
        change_list=True,
        change_form=False,
        label='import new records',
    )
    def import_new_records(self, request):
        try:
            p = Process(
                target=load_run_func,
                args=(LOCK, )
            )
            p.start()
            logger.info(p.is_alive())
            self.message_user(
                request,
                'Запрос на import new records отправлен',
            )
        except Exception as e:
            logger.error(str(e), exc_info=True)
            self.message_user(
                request,
                f'Неизвестная ошибка при import new records документа: {e}',
                messages.ERROR
            )

    @button(
        change_list=True,
        change_form=False,
        label='remove expired records',
    )
    def remove_expired(self, request):
        try:
            call_command('remove_expired')
            # p = Process(
            #     target=remove_run_func,
            #     args=(LOCK, )
            # )
            # p.start()
            # logger.info(p.is_alive())
            self.message_user(
                request,
                'очистка выполнена',
            )
        except Exception as e:
            logger.error(str(e), exc_info=True)
            self.message_user(
                request,
                f'Неизвестная ошибка при remove old records документа: {e}',
                messages.ERROR
            )
