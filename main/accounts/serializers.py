from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "phone_number",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
        ]
