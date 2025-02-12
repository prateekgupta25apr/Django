from django.urls import path

from . import sync_views as sv
from . import async_views as av

urlpatterns = [
    path('async/get_file', av.get_file),
    path('async/upload_file', av.upload_file),
    path('async/delete_file', av.delete_file),
    path('async/get_pre_signed_url', sv.pre_signed_url),

    path('sync/get_file', sv.get_file),
    path('sync/upload_file', sv.upload_file),
    path('sync/delete_file', sv.delete_file),
    path('sync/get_pre_signed_url', sv.pre_signed_url),
    path('sync/get_email_content', sv.get_email_content),
]
