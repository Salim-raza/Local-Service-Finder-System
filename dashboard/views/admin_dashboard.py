from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permission import IsAdmin
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.models import CustomUser
from accounts.serializers import UserCreateSerializers

@api_view(["GET"])
def admin_panel(request):
    return Response({
        "message": "welcome to admin dashboard"
    }, status=status.HTTP_200_OK)


   
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
    method="GET",
    Response={200: "total activate account"}, 
    operation_description="total activate account count"
)
@api_view(["GET"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def total_activate_account_count(request):
    account =  CustomUser.objects.filter(role="SERVICE_PROVIDER", status="accepted").count()
    return Response(account, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method="GET",
    Response={200: "total activate account"}, 
    operation_description="total activate account count"
)
@api_view(["GET"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def total_activate_pending_count(request):
    account =  CustomUser.objects.filter(role="SERVICE_PROVIDER", is_approved=False).count()
    return Response(account, status=status.HTTP_200_OK)