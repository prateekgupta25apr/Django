from django.urls import path

from . import cryptography_async_views as av
from . import cryptography_sync_views as sv

urlpatterns = [
    path('async/des_encrypt', av.des_encrypt_request),
    path('async/des_decrypt', av.des_decrypt_request),
    path('async/hash_sha_256', av.hash_sha_256_request),
    path('async/hmac_sha_256', av.hmac_sha_256_request),
    path('async/aes_encrypt', av.aes_encrypt_request),
    path('async/aes_decrypt', av.aes_decrypt_request),


    path('sync/des_encrypt', sv.des_encrypt_request),
    path('sync/des_decrypt', sv.des_decrypt_request),
    path('sync/hash_sha_256', sv.hash_sha_256_request),
    path('sync/hmac_sha_256', sv.hmac_sha_256_request),
    path('sync/aes_encrypt', sv.aes_encrypt_request),
    path('sync/aes_decrypt', sv.aes_decrypt_request),
]