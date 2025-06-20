from django.urls import path

from . import views

urlpatterns = [
    path('test', views.test),
    path('health_check', views.health_check),
    path('rotate_log_files', views.rotate_log_files_request),
    path('load_config_values', views.load_config_values),
    path('render_html', views.render_html),
]