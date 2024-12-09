from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "customer-login-register-otp/",
        views.customer_login_register_otp,
        name="customer_login_register_otp",
    ),
    path(
        "customer-login-register/",
        views.customer_login_register,
        name="customer_login_register",
    ),
    path("logout/", views.logout, name="logout"),
    path(
        "admin-register-otp/",
        views.admin_register_otp,
        name="admin_register_otp",
    ),
    path("admin-register/", views.admin_register, name="admin_register"),
    path(
        "admin-login-step1/",
        views.admin_login_step_1,
        name="admin_login_step_1",
    ),
    path(
        "admin-login-step2/",
        views.admin_login_step_2,
        name="admin_login_step_2",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
