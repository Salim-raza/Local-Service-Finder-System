from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.permission import IsAdmin
from rest_framework import status
from drf_yasg import openapi
from locations.serializers import *



# Create your views here.
@swagger_auto_schema(
    method="POST",
    request_body=districtSerializers,
    responses={201: districtSerializers(many=False), 400: 'Bad Request'},
    operation_description="create district"
)
@api_view(["POST"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def create_district(request):
    serializer = districtSerializers(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({
        "status": "success",
        "division": serializer.data
    }, status=status.HTTP_201_CREATED)
    
@swagger_auto_schema(
    method="PATCH",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="division id",
            type=openapi.TYPE_INTEGER
        )
    ],
    request_body=districtSerializers,
    responses={200: districtSerializers(many=False), 400: 'Bad Request'},
    operation_description="update district"
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def update_district(request, pk):
    district = get_object_or_404(District, pk=pk)
    serializers = districtSerializers(district, data=request.data, partial=True)
    serializers.is_valid(raise_exception=True)
    serializers.save()
    return Response({
        "status": "success",
        "division": serializers.data
    }, status=status.HTTP_200_OK)
    
@swagger_auto_schema(
    method="DELETE",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="district id",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={204: openapi.Response(description="district deleted successfully"), 400: 'Bad Request'},
    operation_description="delete district"
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def delete_district(request, pk):
    district = get_object_or_404(District, pk=pk)
    district.delete()
    return Response({"message": "district delete successfully"}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method="GET",
    responses={200: districtSerializers(many=True), 400: "Bad Request"},
    operation_description="district list"
)
@api_view(["GET"])
@permission_classes([AllowAny])
def district_list(request):
    district = District.objects.all()
    serializer = districtSerializers(district, many=True)
    return Response({"district": serializer.data})

