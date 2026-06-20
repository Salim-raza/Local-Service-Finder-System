from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from accounts.permission import IsAdmin
from rest_framework import status
from drf_yasg import openapi
from .serializers import *
from .models import *


# Create your views here.
@swagger_auto_schema(
    method="GET",
    responses={200: CreateCategorySerializers(many=True)},
    operation_description="all category"
)
@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    category = Category.objects.all()
    serializer = CreateCategorySerializers(category, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method="POST",
    request_body=CreateCategorySerializers,
    responses={200: CreateCategorySerializers(), 400: "Bad Request"},
    operation_description="Create Category"
)
@api_view(["POST"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def create_category(request):
    serializer = CreateCategorySerializers(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response({"category": serializer.data}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="PATCH",
    request_body=CategoryUpdateSerializers,
    manual_parameters=[
        openapi.Parameter(
            "id",
            openapi.IN_PATH,
            description="category id",
            type=openapi.TYPE_INTEGER
        )  
    ],
    responses={200: CategoryUpdateSerializers(), 400: "Bad Request"},
    operation_description="update category"
)
@swagger_auto_schema(
    method="DELETE",
    manual_parameters=[
        openapi.Parameter(
            "id",
            openapi.IN_PATH,
            description="category id",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={204: 'Deleted successfully'}
)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def category_modify(request, id):
    if request.method == "PATCH":
        category = get_object_or_404(Category, id=id, user=request.user)
        serializer = CategoryUpdateSerializers(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    if request.method == "DELETE":
        category = get_object_or_404(Category, id=id, user=request.user)
        category.delete()
        return Response({"message": "category delete successful"}, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "search",
            openapi.IN_QUERY,
            description="category search",
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: CreateCategorySerializers(many=True)},
    operation_description="search category"
) 
@api_view(["GET"])
@permission_classes([AllowAny])
def category_search(request):
    query = request.GET.get("search")
    category = Category.objects.filter(
        name__icontains = query
    )
    serializers = CreateCategorySerializers(category, many=True)
    return Response({"category": serializers.data}, status=status.HTTP_200_OK)
    
    
    
    
    
# Electrician (ইলেকট্রিশিয়ান)
# Plumber (প্লাম্বার)
# Cleaner (ক্লিনার/পরিষ্কার-পরিচ্ছন্নতা)
# Carpenter (কার্পেন্টার/কাঠমিস্ত্রি)
# Painter (পেইন্টার/রংমিস্ত্রি)
# AC Technician (এসি মেকানিক)
# Appliance Repair (ইলেকট্রনিক্স সার্ভিস)
# Pest Control (পোকামাকড় নিয়ন্ত্রণ)
# Home Shifting / Movers (বাসা পরিবর্তন সার্ভিস)
# Security Guard Service (নিরাপত্তা প্রহরী)