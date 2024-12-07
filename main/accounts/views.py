from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.utils.timezone import now, timedelta
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .models import OTPRequest, CustomUser
from .utils import generate_otp, send_sms


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    phone_number = request.data.get("phone_number")
    if not phone_number:
        return Response(
            {"detail": "phone_number is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not (
        phone_number.startswith("+")
        and phone_number[1:].isdigit()
        and 10 <= len(phone_number) <= 15
    ):
        return Response(
            {
                "detail": "Phone number must be in the format:"
                " '+999999999'. Up to 15 digits allowed."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    otp_request, _ = OTPRequest.objects.get_or_create(
        phone_number=phone_number
    )
    if otp_request.otp_attemps >= 3 and now() < otp_request.otp_attemps_expiry:
        return Response(
            {
                "detail": "Max OTP attempts exceeded."
                f"Try again after {otp_request.otp_attemps_expiry}."
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    otp_request.otp_attemps += 1
    if now() >= otp_request.otp_attemps_expiry:
        otp_request.otp_attemps = 1

    otp_request.otp_attemps_expiry = now() + timedelta(minutes=30)
    otp_request.otp_code = generate_otp()
    otp_request.otp_expiry = now() + timedelta(minutes=5)
    otp_request.save()

    send_sms(otp_request.phone_number, otp_request.otp_code)
    return Response(
        {"detail": "OTP sent successfully."},
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def login_register(request):
    if True in (
        request.data.get("is_staff"),
        request.data.get("is_superuser"),
    ):
        return Response(
            {"detail": "You can't create admin/staff with this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )
    phone_number = request.data.get("phone_number")
    otp_code = request.data.get("otp_code")

    if not phone_number or not otp_code:
        return Response(
            {"detail": "phone_number and otp_code are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp_request = OTPRequest.objects.filter(phone_number=phone_number).first()

    if not otp_request:
        return Response(
            {"detail": "OTP request not found for this phone number."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if now() > otp_request.otp_expiry:
        return Response(
            {"detail": "OTP has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp_request.otp_code != otp_code:
        return Response(
            {"detail": "Invalid OTP."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user:
        user = CustomUser.objects.create_user(phone_number=phone_number)

    otp_request.reset_otp()
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get("refresh_token")
    if not refresh_token:
        return Response(
            {"detail": "Refresh token required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = RefreshToken(refresh_token)
    token.blacklist()
    return Response(
        {"detail": "Successfully logged out."},
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_admin(request):
    if False in (request.user.is_authenticated, request.user.is_superuser):
        return Response(
            {"detail": "You don't have permission to create admin/staff."},
            status=status.HTTP_403_FORBIDDEN,
        )
    if not request.data.get("password", False):
        return Response(
            {"detail": "Admin/Staff members must have a password."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
