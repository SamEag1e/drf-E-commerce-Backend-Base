from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("login-register/", views.login_register, name="login_register"),
    path("logout/", views.logout, name="logout"),
    path("register-admin/", views.register_admin, name="register_admin"),
    path(
        "login-admin-step1/",
        views.login_admin_step_1,
        name="login_admin_step_1",
    ),
    path(
        "login-admin-step2/",
        views.login_admin_step_2,
        name="login_admin_step_2",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
