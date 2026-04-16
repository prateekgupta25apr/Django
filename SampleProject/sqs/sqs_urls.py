from django.urls import path
from . import sqs_sync_views as sv

urlpatterns = [
    path('sync/get_all_queues', sv.get_all_queues_request),
    path('sync/send_message', sv.send_message_request),
]
