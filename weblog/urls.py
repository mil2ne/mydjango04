from django.urls import path
from . import views

app_name = "weblog"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.post_new, name="post_new"),
    path("<int:pk>/", views.post_detail, name="post_detail"),
    path("edit/<int:pk>/", views.post_edit, name="post_edit"),
    path("delete/<int:pk>/", views.post_delete, name="post_delete"),
]
