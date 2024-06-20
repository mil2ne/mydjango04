from django.urls import path
from . import views

app_name = "weblog"

urlpatterns = [
    path("new/", views.post_new, name="post_new"),
    path("<int:pk>/", views.post_detail, name="post_detail"),
    path("edit/<int:pk>/", views.post_edit, name="post_edit"),
]
