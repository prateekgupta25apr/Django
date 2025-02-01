from django.urls import path

from . import views

urlpatterns = [
    path('upload_file', views.upload_file),
    path('delete_file', views.delete_file),
    path('get_email_content', views.get_email_content),
    path('get_file', views.get_file),
]
