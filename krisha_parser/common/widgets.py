from django.forms.widgets import Select


class SelectWithAutocomplete(Select):
    template_name = 'admin/widgets/select_custom.html'
