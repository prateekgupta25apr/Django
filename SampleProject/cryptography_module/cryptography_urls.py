from django.urls import path

from . import cryptography_sync_views

urlpatterns = [
    path('des_encrypt', views.des_encrypt_request)
]