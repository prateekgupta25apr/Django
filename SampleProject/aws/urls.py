from django.urls import path

from . import views

urlpatterns = [
    path('upload_file', views.upload_file),
    path('delete_file', views.delete_file),
]
