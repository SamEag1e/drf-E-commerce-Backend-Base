from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login-otp/", views.customer_login_otp, name="login_otp"),
    path("login/", views.customer_login, name="login"),
    path("add-admin-otp/", views.add_admin_otp, name="add_admin_otp"),
    path("add-admin/", views.add_admin, name="add_admin"),
    path(
        "admin-login-step-1/",
        views.admin_login_step_1,
        name="admin_login_step_1",
    ),
    path(
        "admin-login-step-2/",
        views.admin_login_step_2,
        name="admin_login_step_2",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("logout/", views.logout, name="logout"),
]
