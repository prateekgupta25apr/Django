from django.urls import path

import users.users_views as views

urlpatterns = [
    path("login", views.login, name="login"),
    path("sign_up", views.sign_up, name="sign_up"),
    path("logout", views.logout, name="logout"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("reset_password", views.reset_password, name="reset_password"),
    path("delete_user", views.delete_user, name="delete_user"),
    path("change_password", views.change_password, name="change_password"),
    path("get_user_details", views.get_user_details, name="get_user_details"),
    path("save_user_details", views.save_user_details, name="save_user_details"),
]
