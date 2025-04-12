from django.urls import path

from . import kafka_sync_views,kafka_async_views

urlpatterns = [
    path('async/send', kafka_async_views.send_message_request),
    path('async/get_all_topics', kafka_async_views.get_all_topics_request),
    path('async/get_topic', kafka_async_views.get_topic_request),
    path('async/get_committed_offset', kafka_async_views.get_committed_offset_request),
    path('async/get_messages', kafka_async_views.get_messages_request),


    path('sync/send', kafka_sync_views.send_message_request),
    path('sync/get_all_topics', kafka_sync_views.get_all_topics_request),
    path('sync/get_topic', kafka_sync_views.get_topic_request),
    path('sync/create_topic', kafka_sync_views.create_topic_request),
    path('sync/update_topic_increase_partition',
         kafka_sync_views.update_topic_increase_partition_request),
    path('sync/update_topic', kafka_sync_views.update_topic_request),
    path('sync/delete_topic', kafka_sync_views.delete_topic_request),
    path('sync/get_committed_offset', kafka_sync_views.get_committed_offset_request),
    path('sync/get_messages', kafka_sync_views.get_messages_request),
]
