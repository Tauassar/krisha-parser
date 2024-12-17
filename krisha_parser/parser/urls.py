from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "parser"

urlpatterns = [
    path(
        "approve/",
        TemplateView.as_view(template_name="ui/approve.html"),
        name="approve",
    ),
    path(
        "view/",
        TemplateView.as_view(template_name="ui/view.html"),
        name="approve",
    ),
    path("record/random/", views.random_id),
    path("record/random/approved/", views.random_approved_id),
    path("record/<str:record_id>/", views.record_data),
    path("record/<str:record_id>/like/", views.like),
    path("record/<str:record_id>/dislike/", views.dislike),
]
