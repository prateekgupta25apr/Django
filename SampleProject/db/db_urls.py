from django.urls import path

from . import db_async_views as av
from . import db_sync_views as sv

urlpatterns = [
    path('async/get_data', av.get_data_request),
    path('async/save_data', av.save_data_request),
    path('async/update_data', av.update_data_request),
    path('async/partial_update_data', av.partial_update_data_request),
    path('async/delete_data/<int:primary_key>', av.delete_data_request),

    path('sync/get_data', sv.get_data_request),
    path('sync/save_data', sv.save_data_request),
    path('sync/update_data', sv.update_data_request),
    path('sync/partial_update_data', sv.partial_update_data_request),
    path('sync/delete_data/<int:primary_key>', sv.delete_data_request),
]