from django.urls import path

from . import redis_sync_views,redis_async_views

urlpatterns = [
    path('async/get', redis_async_views.get_request),
    path('async/upsert', redis_async_views.upsert_request),
    path('async/search_keys', redis_async_views.search_keys_request),
    path('async/delete', redis_async_views.delete_request),


    path('sync/get', redis_sync_views.get_request),
    path('sync/upsert', redis_sync_views.upsert_request),
    path('sync/search_keys', redis_sync_views.search_keys_request),
    path('sync/delete', redis_sync_views.delete_request),
]
