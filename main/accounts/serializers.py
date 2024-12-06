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
            "otp_code",
            "otp_trys",
            "otp_max_try_expiry",
            "otp_expiry",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["date_joined"]

    def create(self, validated_data):
        if validated_data.get("is_superuser"):
            return CustomUser.objects.create_superuser(**validated_data)
        if validated_data.get("is_staff"):
            return CustomUser.objects.create_user(**validated_data)
        return CustomUser.objects.create_user(**validated_data)
