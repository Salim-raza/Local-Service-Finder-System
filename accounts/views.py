from rest_framework.decorators import api_view, authentication_classes, permission_classes 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework import status
from django.conf import settings
from .permission import IsAdmin
from drf_yasg import openapi
from .serializers import *
from .models import *
from .utils import *
import random


# Create your views here.
@swagger_auto_schema(
    method='POST',
    request_body=UserCreateSerializers,
    responses={201: UserCreateSerializers(many=False), 400: 'Bad Request'},
    operation_description="user signup"
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializers = UserCreateSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    user = serializers.save()
    
    if user.role == "SERVICE_PROVIDER":
        user.is_approved = False
        user.is_active = False
        message = "service provider request sent to admin"
        token = None
            
    else:
        user.is_approved = True
        user.is_active = True
        message = "signup successfully"
        token = get_tokens_for_user(user)
        
    user.save()
    return Response({
        "message": message,
        "user": UserCreateSerializers(user).data,
        "token": token
        }, status=status.HTTP_201_CREATED)
    
@swagger_auto_schema(
    method="patch",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="user id",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={
        200: openapi.Response(description="Account activated successfully"),
        400: openapi.Response(description="This user does not require approval"),
        404: openapi.Response(description="User not found")
    }
) 
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def pending_account_active(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user.is_approved:
        return Response({"error": "User already approved"},
            status=status.HTTP_400_BAD_REQUEST)
    
    if user.role != "SERVICE_PROVIDER":
        return Response(
            {"error": "This user does not require approval"},
            status=status.HTTP_400_BAD_REQUEST)
        
    user.is_approved = True
    user.is_active = True
    user.save()
    return Response({"message": "account activate"}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method="get",
    responses={200: UserCreateSerializers(many=True), 400: "Bad Request"},
    operation_description="get all pending account"
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdmin])
def pending_account_list(request):
    
    users = CustomUser.objects.filter(
        role="SERVICE_PROVIDER",
        is_approved=False,
        is_active=False
    )
    
    serializer = UserCreateSerializers(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=SigninSerializers,
    responses={201: SigninSerializers(many=False), 400: 'Bad Request'},
    operation_description="user signin"
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signin(request):
    serializers = SigninSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    
    user = authenticate(
        email = serializers.validated_data["email"],
        password = serializers.validated_data["password"]
    )
    
    if user is not None:
        token = get_tokens_for_user(user)
        return Response({"message": "Login Successfully .", "access_token" : token["access"], "refresh_token": token["refresh"]}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid Email OR Password."}, status=status.HTTP_400_BAD_REQUEST)


logout_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh'],
    properties={
        'refresh': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Refresh token"
        )
    }
)

@swagger_auto_schema(
    method="post",
    request_body=logout_request,
    responses={205: openapi.Response(description="logout successfully"),
               400: openapi.Response(description="bad request")},
    operation_description="logout api"
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def signout(request):
    refresh_token = request.data.get("refresh")
    if refresh_token is None:
        return Response(
            {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
    token = RefreshToken(refresh_token)
    token.blacklist()
    return Response(
        {"message": "Logout successful"},
        status=status.HTTP_205_RESET_CONTENT
    )

@swagger_auto_schema(
    method="POST",
    request_body=ChangePasswordSerializers,
    responses={200: ChangePasswordSerializers(many=True), 400: 'Bad Request'},
    operation_description="change password"
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def change_password(request):
    serializers = ChangePasswordSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    
    user = get_object_or_404(CustomUser, id=request.user.id)
    if user.check_password(serializers.validated_data["old_password"]):
        user.set_password(serializers.validated_data["new_password"])
        user.save()
        return Response({"message": "Change password successful."}, status=status.HTTP_200_OK)
    return Response({"message": "Wrong Old Password."}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="POST",
    request_body=OtpCreateSerializers,
    responses={200: OtpCreateSerializers(many=True), 400: 'Bad Request'},
    operation_description= "send otp"
)
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    serializers = OtpCreateSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    
    email = serializers.validated_data["email"]
    
    
    if CustomUser.objects.filter(email=email).exists():
        user = CustomUser.objects.get(email=email)
        otp = random.randint(2222, 9999)
        
        OTP.objects.update_or_create(user=user, defaults={'otp': otp, 'create_at': timezone.now()})
        
        plain_message = f"This is plain message. Your OTP is {otp}. id will expire in 5 minutes."
        
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#f9f9f9; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1);": <h2 style="color:#333;">Password Reset OTP</h2>
        <p>Hello {email},</p>
        <p>Your One-Time Password (OTP) is:</p>
        <h1 style="color:#007bff; letter-spacing:5px;">{otp}</h1>
        <p>This code is valid for <b>5 minutes</b>. Do not share it with anyone.</p>
        <p style="font-size:12px; color:#888;">If you didn't request this, please ignore this email.</p>
        </div>
        </body> </html>
        """
        
        
        send_mail(
            subject="Reset Password OTP",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[serializers.validated_data['email']],
            fail_silently=False,
            html_message=html_message
        )
        
        return Response({
            "status": "success",
            "message": "OTP Send Successfully to Your Gmail",
        }, status=status.HTTP_201_CREATED)
        
    return Response({
        "status": "failed",
        "message": "email doesnot exists",
    }, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method="POST",
    request_body=RestPasswordSerializers,
    responses={200: RestPasswordSerializers(many=True), 400: 'Bad Request'},
    operation_description="Reset password"
)
@api_view(["POST"])
@permission_classes([AllowAny])
def rest_password(request):
    serializers = RestPasswordSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    
    email = serializers.validated_data["email"]
    otp = serializers.validated_data["otp"]
    new_password = serializers.validated_data["new_password"]
    
    
    if CustomUser.objects.filter(email=email).exists():
        user = CustomUser.objects.get(email__iexact=email)
        db_otp = OTP.objects.filter(user=user).last()

        if db_otp and str(otp) == str(db_otp.otp):

            if db_otp.is_expire:
                return Response({
                    "status": "error",
                    "message": "otp time expired"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({
                "status": "success",
                "message": "password reset successful"
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "failed",
            "message": "wrong otp"
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "failed",
        "message": "email does not exists."
    }, status=status.HTTP_400_BAD_REQUEST)
