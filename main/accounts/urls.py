from django.urls import path
from . import views

urlpatterns = [
    path("send_otp/", views.send_otp, name="send_otp"),
    # path("logout/", views.logout, name="logout"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    # path("register_admin/", views.register_admin, name="register_admin"),
    # path("login_admin/", views.login_admin, name="login_admin"),
    # path("profile/", views.profile, name="profile"),
]
