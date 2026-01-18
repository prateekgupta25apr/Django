from django.urls import path

from . import emails_sync_views as sv
from . import emails_async_views as av

urlpatterns = [
    path('async/get_email_content', av.get_email_content),
    path('async/send_email', av.send_email),
    path('async/process_email', sv.process_email_request),

    path('sync/get_email_content', sv.get_email_content),
    path('sync/send_email', sv.send_email),
    path('sync/process_email', sv.process_email_request),
]
