from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from accounts.permission import IsAdmin
from rest_framework import status
from drf_yasg import openapi
from serializers import *


# Create your views here.
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