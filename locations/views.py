from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from accounts.permission import IsAdmin
from rest_framework import status
from drf_yasg import openapi
from .serializers import *

# Create your views here.
@swagger_auto_schema(
    method="POST",
    request_body=divisionSerializers,
    responses={201: divisionSerializers(many=False), 400: 'Bad Request'},
    operation_description="create division"
)
@api_view(["POST"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def create_division(request):
    serializers = divisionSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    serializers.save()
    return Response({
        "status": "success",
        "division": serializers.data
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
    request_body=divisionSerializers,
    responses={200: divisionSerializers(many=False), 400: 'Bad Request'},
    operation_description="update division"
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def update_division(request, pk):
    division = get_object_or_404(Division, pk=pk, user=request.user)
    serializers = divisionSerializers(division, data=request.data, partial=True)
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
            description="division id",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={204: openapi.Response(description="division deleted successfully"), 400: 'Bad Request'},
    operation_description="delete division"
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def delete_division(request, pk):
    division = get_object_or_404(Division, pk=pk)
    division.delete()
    return Response({"message": "division delete successfully"}, status=status.HTTP_204_NO_CONTENT)


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
    district = get_object_or_404(District, pk=pk, user=request.user)
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
    method="POST",
    request_body=upazilaSerializers,
    responses={201: upazilaSerializers(many=True), 400: "bad request"},
    operation_description="create upazila"
)
@api_view(["POST"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def create_upazila(request):
    serializer = upazilaSerializers(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({
        "status": "success",
        "upazila": serializer.data
    }, status=status.HTTP_201_CREATED)
    

@swagger_auto_schema(
    method="PATCH",
    manual_parameters=[
        openapi.Parameter(
            "pk",
            openapi.IN_PATH,
            description="update upazila",
            type=openapi.TYPE_INTEGER
        )
    ],
    request_body=upazilaSerializers,
    responses={200: upazilaSerializers(many=True), 400: "Bad request"},
    operation_description="update upazila"
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def update_upazila(request, pk):
    upazila = get_object_or_404(Upazila, pk=pk)
    serializer = upazilaSerializers(upazila, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"status": "success", "upazila" : serializer.data}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="DELETE",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="upazila id",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={204: openapi.Response("delete upazila"), 400: "bad request"},
    operation_description="delete upazila"
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def delete_upazila(request, pk):
    upazila = get_object_or_404(Upazila, pk=pk)
    upazila.delete()
    return Response({"message": "upazila delete successfully"}, status=status.HTTP_204_NO_CONTENT)