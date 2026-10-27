from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from accounts.permission import IsAdmin
from rest_framework import status
from drf_yasg import openapi
from locations.serializers import *

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
    division = get_object_or_404(Division, pk=pk)
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
    method="GET",
    responses={200: divisionSerializers(many=True), 400: 'Bad Request'},
    operation_description="get all division"
)
@api_view(["GET"])
@permission_classes([AllowAny])
def division_list(request):
    division = Division.objects.all()
    serializer = divisionSerializers(division, many=True)
    return Response({"division": serializer.data})
