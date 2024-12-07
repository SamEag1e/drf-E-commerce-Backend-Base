from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("send_otp/", views.send_otp, name="send_otp"),
    path("login_register/", views.login_register, name="login_register"),
    path("logout/", views.logout, name="logout"),
    # path("register_admin/", views.register_admin, name="register_admin"),
    # path("login_admin/", views.login_admin, name="login_admin"),
    # path("profile/", views.profile, name="profile"),
]
