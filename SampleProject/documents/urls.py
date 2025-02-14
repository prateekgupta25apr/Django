from django.urls import path

from . import views

urlpatterns = [
    path('excel_to_json', views.excel_to_json),
]
