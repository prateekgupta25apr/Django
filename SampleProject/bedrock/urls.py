from django.urls import path

from . import bedrock_sync_views as sv
from . import bedrock_async_views as av

urlpatterns = [
    path('async/generate_embedding_for_image', av.generate_embedding_for_image_request),
    path('async/generate_embedding_for_text', av.generate_embedding_for_text_request),

    path('sync/generate_embedding_for_image', sv.generate_embedding_for_image_request),
    path('sync/generate_embedding_for_text', sv.generate_embedding_for_text_request),
]
