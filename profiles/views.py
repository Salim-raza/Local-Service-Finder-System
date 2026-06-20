from rest_framework.decorators import api_view, permission_classes, authentication_classes
from accounts.permission import IsAdmin, IsServiceProvider, IsAdminORServiceProvider, IsCustomer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ProfileSerializer, ProfileUpdateSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from .pagination import ProfilePagination
from rest_framework import status
from drf_yasg import openapi
from .models import Profile


# Create your views here.
@swagger_auto_schema(
    method='GET',
    responses={200: ProfileSerializer(many=True)},
    operation_description='Get all user profiles'
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_profiles(request):
    try:
        profile = Profile.objects.all()
        pagination = ProfilePagination()
        result_page = pagination.paginate_queryset(profile, request)
        serializers = ProfileSerializer(result_page, many=True)
        return Response({"profile": serializers.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@swagger_auto_schema(
    method='GET',
    responses={200: ProfileSerializer()},
    operation_description='Get user profile'
)
@api_view(["GET"])
@permission_classes([IsAdminORServiceProvider | IsCustomer])
@authentication_classes([JWTAuthentication])
def get_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        serializers = ProfileSerializer(profile)
        return Response({"profile": serializers.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
 
@swagger_auto_schema(
    method='PATCH',
    request_body=ProfileUpdateSerializer,
    responses={200: ProfileUpdateSerializer()},
    operation_description='Update user profile'
)
@swagger_auto_schema(
    method='DELETE',
    responses={204: 'Profile deleted successfully'},
    operation_description='Delete user profile'
)    
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminORServiceProvider | IsCustomer])
@authentication_classes([JWTAuthentication])
def modify_profile(request):
    if request.method == "PATCH":
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "profile": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "DELETE":
        try:
            profile = Profile.objects.get(user=request.user)
            profile.delete()
            return Response({"message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@swagger_auto_schema(
    method='GET',
    manual_parameters=[
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description="Search query for profiles",
            type=openapi.TYPE_STRING
        ),
    ]
)
@api_view(["GET"])
@permission_classes([AllowAny])
def search_profile(request):
    query = request.GET.get("search")
    profile = Profile.objects.filter(
        user__first_name__icontains=query
    ) | Profile.objects.filter(
        user__last_name__icontains=query
    ) | Profile.objects.filter(
        city__icontains=query
    ) | Profile.objects.filter(
        area__icontains=query
    )
    pagination = ProfilePagination()
    result_page = pagination.paginate_queryset(profile, request)
    serializers = ProfileSerializer(result_page, many=True)
    return Response({"profile": serializers.data}, status=status.HTTP_200_OK)



