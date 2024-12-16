import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Restaurant
from botocore.exceptions import ClientError
from .serializers import RestaurantSerializer

class RestaurantListView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantDetailView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    def put(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        bank_accounts = restaurant.bank_accounts.all()
        bank_accounts.delete()
        restaurant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class S3PreSignedUrlView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def generate_presigned_url(self, bucket_name, object_name, expiration=3600):
        """
        Generate a pre-signed URL for S3 to allow uploading an object.
        """
        s3_client = boto3.client(
            's3',
             aws_access_key_id= settings.CIVO_BUCKET_ACCESS_KEY,
            aws_secret_access_key=settings.CIVO_BUCKET_SECRET_KEY,
            endpoint_url=f'https://{settings.CIVO_REGION}.object.civo.com'
        )
        try:
            response = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
        except ClientError as e:
            return None, str(e)
        return response, None

    def post(self, request):
        bucket_name = 'zapeat'
        object_key = 'restaurant_logos/restaurant.jpg'  # Customize based on request or logic
        expiration_time = 3600  # URL validity time in seconds

        # Generate the pre-signed URL
        presigned_url, error = self.generate_presigned_url(bucket_name, object_key, expiration_time)

        if error:
            return Response({'error': f'Failed to generate pre-signed URL: {error}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'url': presigned_url}, status=status.HTTP_200_OK)

    def get(self, request):
        return Response({'url': "hjidj"}, status=status.HTTP_200_OK)