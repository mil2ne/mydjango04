from django.urls import path, re_path
from . import converters
from . import views

urlpatterns = [
    path(route="", view=views.index),
    path(route="archives/<date:release_date>/", view=views.index),
    # path(route="export.csv", view=views.export_csv),
    re_path(route=r"^export\.(?P<format>(csv|xlsx))$", view=views.export),
    path(route="<int:pk>/cover.png", view=views.cover_png),
]
