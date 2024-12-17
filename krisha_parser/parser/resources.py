
from import_export import resources, fields
from .models import Record


class RecordResource(resources.ModelResource):
    area = fields.Field(column_name='Площадь', attribute='area')
    plain_link = fields.Field(column_name='Ссылка на крышу', attribute='plain_link')
    residential_complex = fields.Field(column_name='ЖК', attribute='residential_complex')
    description = fields.Field(column_name='Описание', attribute='description')
    curr_floor = fields.Field(column_name='Этаж', attribute='curr_floor')
    post_date = fields.Field(column_name='Дата публикации', attribute='post_date')
    krisha_created_at = fields.Field(column_name='Дата создания', attribute='krisha_created_at')
    full_address = fields.Field(column_name='Адрес', attribute='full_address')
    changed_at = fields.Field(column_name='Добавлено в файл', attribute='changed_at')

    class Meta:
        model = Record
        fields = [
            'kid',
            'comment',
            'price',
            'area',
            'plain_link',
            'residential_complex',
            'description',
            'curr_floor',
            'post_date',
            'krisha_created_at',
            'full_address',
            'changed_at',
        ]

    def dehydrate_curr_floor(self, obj: Record) -> str:
        return f"{obj.floor} / {obj.max_floor}"
