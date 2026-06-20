from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from accounts.permission import IsAdminORServiceProvider, IsAdmin, IsServiceProvider
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from categories.serializers import CreateCategorySerializers
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from .pagination import MyPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from drf_yasg import openapi
from .serializers import *
from .models import *

# Create your views here.
@swagger_auto_schema(
    method='GET',
    responses={200: ServiceCreateSerializers(many=True)},
    operation_description='all service view'
)
@api_view(["GET"])
@permission_classes([AllowAny])
def all_service(request):
    service = Service.objects.all()
    serializers = ServiceCreateSerializers(service, many=True)
    return Response({"service": serializers.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    responses={200: ServiceCreateSerializers(many=True)},
    operation_description="Uer service view"
)
@swagger_auto_schema(
    method='POST',
    request_body=ServiceCreateSerializers,
    responses={201: ServiceCreateSerializers(), 400: 'Bad Request'},
    operation_description="Service Create"
)

@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsServiceProvider])
@parser_classes([MultiPartParser, FormParser])
def service(request):
    if request.method == "GET":
        service = Service.objects.filter(provider=request.user)
        serializer = ServiceCreateSerializers(service, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        serializer = ServiceCreateSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=request.user)
        return Response({
            "status": "success",
            "service": serializer.data
        }, status=status.HTTP_201_CREATED)
  
  
        
@swagger_auto_schema(
    method='PATCH',
    request_body=ServiceUpdateSerializers,
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="Service ID",
            type=openapi.TYPE_INTEGER,
    )
    ],
    responses={200: ServiceUpdateSerializers(many=False), 400: 'Bad Request'},
    operation_description="Service Update"
)
@swagger_auto_schema(
    method='DELETE',
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="Service ID",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={204: 'Deleted successfully'}
)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminORServiceProvider])
@authentication_classes([JWTAuthentication])
def service_modify(request, id):
    if request.method == "PATCH":
        service = get_object_or_404(Service, id=id, provider=request.user)
        serializers = ServiceUpdateSerializers(service, data=request.data, partial=True)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(
            {
                "status": "success",
                "message": "service update success",
                "service": serializers.data   
            }, status=status.HTTP_200_OK)
        
    elif request.method == "DELETE":
        service = get_object_or_404(Service, id=id)
        service.delete()
        return Response({"message": " service delete successfully"}, status=status.HTTP_200_OK)


  
@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description="search query",
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: ServiceCreateSerializers(many=True)}
)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_service(request):
    query = request.GET.get("search")
    if not query:
        return Response({"message": "query missing"}, status=status.HTTP_400_BAD_REQUEST)
    services = Service.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query)|
        Q(category__name__icontains=query)|
        Q(provider__district__name__icontains=query)|
        Q(provider__upazila__name__icontains=query)|
        Q(provider__area__name__icontains=query)
    ).order_by('id')
    if not services.exists():
        return Response({"detail": "Service Not Found"}, status=status.HTTP_404_NOT_FOUND)
    pagination = MyPageNumberPagination()
    paginated = pagination.paginate_queryset(services, request)
    serializer = ServiceCreateSerializers(paginated, many=True)
    return pagination.get_paginated_response(serializer.data)
