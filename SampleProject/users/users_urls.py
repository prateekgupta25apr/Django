from django.urls import path

from . import users_async_views as av
from . import users_sync_views as sv

urlpatterns = [
    path("async/login", av.login, name="async_login"),
    path("async/sign_up", av.sign_up, name="async_sign_up"),
    path("async/logout", av.logout, name="async_logout"),
    path("async/forgot_password", av.forgot_password, name="async_forgot_password"),
    path("async/reset_password", av.reset_password, name="async_reset_password"),
    path("async/delete_user", av.delete_user, name="async_delete_user"),
    path("async/change_password", av.change_password, name="async_change_password"),
    path("async/get_user_details", av.get_user_details, name="async_get_user_details"),
    path("async/save_user_details", av.save_user_details, name="async_save_user_details"),

    path("sync/login", sv.login, name="sync_login"),
    path("sync/sign_up", sv.sign_up, name="sync_sign_up"),
    path("sync/logout", sv.logout, name="sync_logout"),
    path("sync/forgot_password", sv.forgot_password, name="sync_forgot_password"),
    path("sync/reset_password", sv.reset_password, name="sync_reset_password"),
    path("sync/delete_user", sv.delete_user, name="sync_delete_user"),
    path("sync/change_password", sv.change_password, name="sync_change_password"),
    path("sync/get_user_details", sv.get_user_details, name="sync_get_user_details"),
    path("sync/save_user_details", sv.save_user_details, name="sync_save_user_details"),
]
