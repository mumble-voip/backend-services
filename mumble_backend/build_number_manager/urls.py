from django.urls import path

from . import views

urlpatterns = [
    path("", views.nothing, name="nothing"),
    path("/", views.nothing, name="nothing"),
    path("/v", views.nothing, name="nothing"),
    path("/v/", views.nothing, name="nothing"),
    path("/v<int:version>", views.version, name="version"),
    path("/v<int:version>/", views.version, name="version"),
    path("/v<str:version>", views.version, name="version"),
    path("/v<str:version>/", views.version, name="version"),
    path("/<str:version>", views.version, name="invalid_version"),
    path("/<str:version>/", views.version, name="invalid_version"),
    path(
        "/v<int:version>/<str:series>", views.version_series, name="version and series"
    ),
    path(
        "/v<int:version>/<str:series>/", views.version_series, name="version and series"
    ),
    path(
        "/v<int:version>/<str:series>/<str:commit>",
        views.version_series_commit,
        name="version, series and commit",
    ),
    path(
        "/v<int:version>/<str:series>/<str:commit>/",
        views.version_series_commit,
        name="version, series and commit",
    ),
]
