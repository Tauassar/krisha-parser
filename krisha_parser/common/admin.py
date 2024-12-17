import logging
import ast
import json
import typing
import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe
from django import forms
from django.utils.translation import get_language

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer, XmlLexer

from . import widgets


logger = logging.getLogger(__name__)


class PrettyJsonMixin:

    @staticmethod
    def pretty_json(value: str) -> str:
        try:
            obj = json.loads(value)
        except json.JSONDecodeError:
            obj = ast.literal_eval(value)
        return json.dumps(obj, indent=4, ensure_ascii=False)

    @staticmethod
    def pretty_xml(value: str) -> str:
        dom = ET.XML(value)
        ET.indent(dom)
        return ET.tostring(dom, encoding="unicode")

    @staticmethod
    def highlight_json(value: str) -> SafeText:
        return mark_safe(highlight(value, lexer=JsonLexer(),
                                   formatter=HtmlFormatter(noclasses=True, nobackground=True)))

    @staticmethod
    def highlight_xml(value: str) -> SafeText:
        return mark_safe(highlight(value, lexer=XmlLexer(),
                                   formatter=HtmlFormatter(noclasses=True, nobackground=True)))
    @classmethod
    def pretty_raw(cls, obj: str) -> SafeText:
        try:
            return cls.highlight_json(cls.pretty_json(obj))
        except (ValueError, SyntaxError):
            try:
                return cls.highlight_xml(cls.pretty_xml(obj))
            except ET.ParseError:
                return format_html("<pre><code>{}</code></pre>", obj)


class StaticAutocomplete:
    static_autocomplete_fields: typing.Iterable[str] = []

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = ('admin/js/vendor/select2/i18n/%s.js' % i18n_name,) if i18n_name else ()
        return super().media + forms.Media(
            js=(
                'admin/js/vendor/jquery/jquery%s.js' % extra,
                'admin/js/vendor/select2/select2.full%s.js' % extra,
            ) + i18n_file + (
                'admin/js/jquery.init.js',
                'admin/js/autocomplete_static.js',
            ),
            css={
                'screen': (
                    'admin/css/vendor/select2/select2%s.css' % extra,
                    'admin/css/autocomplete.css',
                ),
            },
        )

    def get_static_autocomplete_fields(self, request):
        """
        Return a list of ForeignKey and/or ManyToMany fields which should use
        an autocomplete widget.
        """
        return self.static_autocomplete_fields

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Get a form Field for a database Field that has declared choices.
        """

        # If the field is named as a radio_field, use a RadioSelect
        if db_field.name in self.get_static_autocomplete_fields(request):
            # Avoid stomping on custom widget/choices arguments.
            if 'widget' not in kwargs:
                kwargs['widget'] = widgets.SelectWithAutocomplete()

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """

        # If the field is named as a radio_field, use a RadioSelect
        if db_field.name in self.get_static_autocomplete_fields(request):
            # Avoid stomping on custom widget/choices arguments.
            if 'widget' not in kwargs:
                kwargs['widget'] = widgets.SelectWithAutocomplete()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class FilterListCollapseMixin:
    @property
    def media(self):
        return super().media + forms.Media(
            js=(
                'admin/js/list_filter_collapse.js',
            ),
        )
