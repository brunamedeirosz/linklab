from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/links/",
        views.create_short_link,
        name="create-short-link",
    ),
    path(
        "api/links/<str:code>/stats/",
        views.link_statistics,
        name="link-statistics",
    ),
    path(
        "<str:code>/",
        views.redirect_short_link,
        name="redirect-short-link",
    ),
]