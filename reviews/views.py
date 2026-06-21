from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ReviewAndRatingSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from accounts.permission import IsCustomer
from .models import ReviewAndRating
from service.models import Service
from rest_framework import status
from drf_yasg import openapi
from django.db.models import Avg
# from accounts import models

# Create your views here.
@swagger_auto_schema(
    method="get",
    responses={200: ReviewAndRatingSerializer(many=True), 400: "bad request"},
    operation_description="get review and rating"
)
@api_view(["GET"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def get_review(request, service_id):
    get_object_or_404(Service, id=service_id)
    reviews = ReviewAndRating.objects.filter(service_id=service_id)
    serializer = ReviewAndRatingSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method="POST",
    request_body=ReviewAndRatingSerializer,
    responses={201: ReviewAndRatingSerializer(), 400: "bd request"},
    operation_description="create review and rating"
)
@api_view(["POST"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def create_review_rating(request):
    serializer = ReviewAndRatingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="patch",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="review and rating id",
            type=openapi.TYPE_INTEGER
        )
    ],
    request_body=ReviewAndRatingSerializer,
    responses={200: ReviewAndRatingSerializer(many=True), 400: "bad request"},
    operation_description="update review and rating"
)
@api_view(["PATCH"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_review_rating(request, pk):
    review = get_object_or_404(ReviewAndRating, user=request.user, pk=pk)
    serializer = ReviewAndRatingSerializer(review, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method="delete",
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="review and rating id",
            type=openapi.TYPE_INTEGER
        )
    ],
    operation_description="delete review and rating "
)
@api_view(["DELETE"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def delete_review_rating(request, pk):
    review = get_object_or_404(ReviewAndRating, pk=pk, user=request.user)
    review.delete()
    return Response({"details": "review delete successfully"}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="GET",
    responses={200: ReviewAndRatingSerializer(many=True), 400: "bad request"},
    operation_description="Get average Reviews and Ratings",
    manual_parameters=[
        openapi.Parameter(
            'service_id',
            openapi.IN_PATH,
            description="Service ID",
            type=openapi.TYPE_INTEGER
        )
    ],
    
)
@api_view(["GET"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def get_average_review_rating(request, service_id):
    get_object_or_404(Service, id=service_id)
    reviews = ReviewAndRating.objects.filter(service_id=service_id)
    average_rating = reviews.aggregate(average_rating=Avg('rating'))['average_rating']
    return Response({"average_rating": average_rating}, status=status.HTTP_200_OK)