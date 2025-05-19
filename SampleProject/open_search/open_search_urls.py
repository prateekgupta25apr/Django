from django.urls import path

from . import open_search_sync_views,open_search_async_views

urlpatterns = [
    path('async/get_index', open_search_async_views.get_index_request),


    path('sync/get_index', open_search_sync_views.get_index_request),

]
