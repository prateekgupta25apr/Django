from django.urls import path

from . import cryptography_async_views as av
from . import cryptography_sync_views as sv

urlpatterns = [
    path('async/des_encrypt', av.des_encrypt_request),
    path('async/des_decrypt', av.des_decrypt_request),


    path('sync/des_encrypt', sv.des_encrypt_request),
    path('sync/des_decrypt', sv.des_decrypt_request)
]