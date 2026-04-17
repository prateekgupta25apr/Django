from django.urls import path
from . import sqs_sync_views as sv
from . import sqs_async_views as av

urlpatterns = [
    path('async/send_message', av.send_message_request),
    path('async/get_all_queues', av.get_all_queues_request),
    path('async/get_queue', av.get_queue_request),
    path('async/create_queue', av.create_queue_request),
    path('async/update_queue', av.update_queue_request),
    path('async/delete_queue', av.delete_queue_request),
    path('async/add_queue', av.add_queue_request),
    path('async/remove_queue', av.remove_queue_request),
    path('async/get_messages', av.get_messages_request),

    path('sync/send_message', sv.send_message_request),
    path('sync/get_all_queues', sv.get_all_queues_request),
    path('sync/get_queue', sv.get_queue_request),
    path('sync/create_queue', sv.create_queue_request),
    path('sync/update_queue', sv.update_queue_request),
    path('sync/delete_queue', sv.delete_queue_request),
    path('sync/add_queue', sv.add_queue_request),
    path('sync/remove_queue', sv.remove_queue_request),
    path('sync/get_messages', sv.get_messages_request),
]
