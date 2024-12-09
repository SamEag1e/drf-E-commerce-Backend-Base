from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now, timedelta


# ---------------------------------------------------------------------
class OTPRequest(models.Model):
    # -----------------------------------------------------------------
    def default_otp_expiry():
        return now() + timedelta(minutes=5)

    # -----------------------------------------------------------------
    def default_otp_attemps_expiry():
        return now() + timedelta(minutes=30)

    OTP_TYPE_CHOICES = [
        ("customer_login", "Customer Login"),
        ("admin_login", "Admin Login"),
        ("admin_register", "Admin Register"),
        ("password_change", "Password change"),
    ]
    phone_number = models.CharField(max_length=15, unique=True)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_attemps = models.PositiveIntegerField(default=0)

    otp_expiry = models.DateTimeField(default=default_otp_expiry)
    otp_attemps_expiry = models.DateTimeField(
        default=default_otp_attemps_expiry
    )

    # -----------------------------------------------------------------
    def __str__(self):
        return f"OTP for {self.phone_number}"


# ---------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    # -----------------------------------------------------------------
    def create_user(self, phone_number, password=None, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    # -----------------------------------------------------------------
    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self.create_user(
            phone_number=phone_number, password=password, **extra_fields
        )


# ---------------------------------------------------------------------
class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = "phone_number"

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number
