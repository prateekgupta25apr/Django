from django.urls import path

from . import open_search_sync_views,open_search_async_views

urlpatterns = [
    path('async/get_index', open_search_async_views.get_index_request),
    path('async/create_index', open_search_async_views.create_index_request),
    path('async/update_index', open_search_async_views.update_index_request),
    path('async/delete_index', open_search_async_views.delete_index_request),
    path('async/get_record', open_search_async_views.get_record_request),
    path('async/upsert_record', open_search_async_views.upsert_record_request),
    path('async/partial_update_record',
         open_search_async_views.partial_update_record_request),
    path('async/delete_record', open_search_async_views.delete_record_request),


    path('sync/get_index', open_search_sync_views.get_index_request),
    path('sync/create_index', open_search_sync_views.create_index_request),
    path('sync/update_index', open_search_sync_views.update_index_request),
    path('sync/delete_index', open_search_sync_views.delete_index_request),
    path('sync/get_record', open_search_sync_views.get_record_request),
    path('sync/upsert_record', open_search_sync_views.upsert_record_request),
    path('sync/partial_update_record', open_search_sync_views.partial_update_record_request),
    path('sync/delete_record', open_search_sync_views.delete_record_request),

]
