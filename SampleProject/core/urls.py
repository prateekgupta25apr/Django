from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test),
    path('rotate_log_files', views.rotate_log_files_request),
]