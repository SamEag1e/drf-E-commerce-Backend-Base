from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GeneralSettings(models.Model):
    is_ordering_enabled = models.BooleanField(default=True)
    is_full_payment_enabled = models.BooleanField(default=True)
    is_down_payment_enabled = models.BooleanField(default=True)
    is_maintenance_mode = models.BooleanField(default=False)

    maintenance_message = models.TextField(blank=True, null=True)
    order_disabled_message = models.TextField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return "General Settings"
