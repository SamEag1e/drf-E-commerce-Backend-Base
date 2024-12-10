from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.decorators import api_view, permission_classes
from django.utils.timezone import now, timedelta
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .models import OTPRequest, CustomUser
from .utils import generate_otp, send_sms


# ---------------------------------------------------------------------
def _send_otp_check(request, otp_type):
    phone_number = request.data.get("phone_number")
    if not phone_number:
        return (
            False,
            "phone_number is required.",
            status.HTTP_400_BAD_REQUEST,
        )
    if not (
        phone_number.startswith("+")
        and phone_number[1:].isdigit()
        and 10 <= len(phone_number) <= 15
    ):
        return (
            False,
            "Invalid phone number format. Use '+999999999'.",
            status.HTTP_400_BAD_REQUEST,
        )
    otp_request, _ = OTPRequest.objects.get_or_create(
        phone_number=phone_number
    )
    if otp_request.otp_attemps >= 3 and now() < otp_request.otp_attemps_expiry:
        return (
            False,
            f"Max OTP attempts exceeded. Try again after {otp_request.otp_attemps_expiry}.",
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if now() >= otp_request.otp_attemps_expiry:
        otp_request.otp_attemps = 0

    otp_request.otp_type = otp_type
    otp_request.otp_attemps += 1
    otp_request.otp_attemps_expiry = now() + timedelta(minutes=30)
    otp_request.otp_code = generate_otp()
    otp_request.otp_expiry = now() + timedelta(minutes=5)
    otp_request.save()

    send_sms(otp_request.phone_number, otp_request.otp_code)
    return (True, "OTP sent successfully.", status.HTTP_200_OK)


# ---------------------------------------------------------------------
def _veryify_otp(request, otp_type):
    phone_number = request.data.get("phone_number")
    otp_code = request.data.get("otp_code")
    if not phone_number or not otp_code:
        return (
            False,
            "phone_number and otp_code are required.",
            status.HTTP_400_BAD_REQUEST,
        )

    otp_request = OTPRequest.objects.filter(phone_number=phone_number).first()
    if not otp_request:
        return (
            False,
            "OTP request not found for this phone number.",
            status.HTTP_404_NOT_FOUND,
        )

    if now() > otp_request.otp_expiry:
        return (False, "OTP has expired.", status.HTTP_400_BAD_REQUEST)

    if otp_request.otp_type != otp_type:
        return (False, "Invalid otp_type.", status.HTTP_400_BAD_REQUEST)
    if otp_request.otp_code != otp_code:
        return (False, "Invalid OTP.", status.HTTP_400_BAD_REQUEST)
    otp_request.delete()
    return (True, "OTP is valid.", status.HTTP_200_OK)


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def customer_login_otp(request):
    _, detail, status_code = _send_otp_check(request, "customer_login")
    return Response({"detail": detail}, status=status_code)


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def customer_login(request):
    if True in (
        request.data.get("is_staff"),
        request.data.get("is_superuser"),
    ):
        return Response(
            {"detail": "You can't register admin/staff with this endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )
    is_valid, detail, status_code = _veryify_otp(request, "customer_login")
    if not is_valid:
        return Response({"detail": detail}, status_code)

    phone_number = request.data.get("phone_number")
    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user:
        user = CustomUser.objects.create_user(phone_number=phone_number)

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "detail": detail,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status_code,
    )


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login_step_1(request):
    phone_number = request.data.get("phone_number")
    password = request.data.get("password")

    if not phone_number or not password:
        return Response(
            {"detail": "phone_number and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user or not user.is_staff:
        return Response(
            {"detail": "Invalid phone number or not an admin."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if not user.check_password(password):
        return Response(
            {"detail": "Incorrect password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    _, detail, status_code = _send_otp_check(request, "admin_login")
    return Response({"detail": detail}, status=status_code)


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login_step_2(request):
    is_valid, detail, status_code = _veryify_otp(request, "admin_login")

    if not is_valid:
        return Response({"detail": detail}, status=status_code)

    phone_number = request.data.get("phone_number")
    user = CustomUser.objects.filter(
        phone_number=phone_number, is_staff=True
    ).first()
    if not user:
        return Response(
            {"detail": "Admin not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "detail": detail,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status_code,
    )


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_admin_otp(request):
    _, detail, status_code = _send_otp_check(request, "admin_register")
    return Response({"detail": detail}, status=status_code)


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_admin(request):
    phone_number = request.data.get("phone_number")
    password = request.data.get("password")
    is_staff = request.data.get("is_staff", False)
    is_superuser = request.data.get("is_superuser", False)
    if not (is_staff or is_superuser):
        return Response(
            {
                "detail": "You can only register admin/staff with this endpoint."
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    if False in (request.user.is_authenticated, request.user.is_superuser):
        return Response(
            {"detail": "You don't have permission to create admin/staff."},
            status=status.HTTP_403_FORBIDDEN,
        )
    if not password:
        return Response(
            {"detail": "Admin/Staff members must have a password."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    is_valid, detail, status_code = _veryify_otp(request, "admin_register")
    if not is_valid:
        return Response({"detail": detail}, status_code)

    user = CustomUser.objects.filter(phone_number=phone_number).first()
    if not user:
        if is_superuser:
            user = CustomUser.objects.create_superuser(
                phone_number=phone_number, password=password
            )
            return Response(
                {"detail": "Superuser created successfully."},
                status=status.HTTP_201_CREATED,
            )
        user = CustomUser.object.create_user(
            phone_number=phone_number, password=password, is_staff=True
        )
        return Response(
            {"detail": "Staff user created successfully."},
            status=status.HTTP_201_CREATED,
        )
    if is_superuser:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return Response(
            {"detail": "User updated to superuser."},
            status=status.HTTP_201_CREATED,
        )
    user.is_staff = True
    user.save()
    return Response(
        {"detail": "User updated to staff."},
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------
class ProfileView(RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"detail": "Refresh token required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = RefreshToken(refresh_token)
    if token:
        token.blacklist()
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"detail": "Invalid refresh token."},
        status=status.HTTP_400_BAD_REQUEST,
    )
