import boto3
from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from botocore.exceptions import ClientError
from .models import (
    Restaurant,
    MenuCategory,
    MenuItem,
    CustomizationGroup,
    CustomizationOption
)
from .serializers import (
    RestaurantSerializer,
    MenuCategorySerializer,
    MenuItemSerializer,
    CustomizationGroupSerializer,
    CustomizationOptionSerializer,
)
from orders.models import Order
from orders.serializers import OrderSerializer

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
        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
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

# CRUD for MenuCategory
class MenuCategoryAPIView(APIView):

    def get(self, request):
        categories = MenuCategory.objects.all()
        serializer = MenuCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuCategoryDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(MenuCategory, pk=pk)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = MenuCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = MenuCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD for MenuItem
class MenuItemAPIView(APIView):

    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(MenuItem, pk=pk)

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD for CustomizationGroup
class CustomizationGroupAPIView(APIView):

    def get(self, request):
        groups = CustomizationGroup.objects.all()
        serializer = CustomizationGroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomizationGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomizationGroupDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(CustomizationGroup, pk=pk)

    def get(self, request, pk):
        group = self.get_object(pk)
        serializer = CustomizationGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        group = self.get_object(pk)
        serializer = CustomizationGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD for CustomizationOption
class CustomizationOptionAPIView(APIView):

    def get(self, request):
        options = CustomizationOption.objects.all()
        serializer = CustomizationOptionSerializer(options, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomizationOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomizationOptionDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(CustomizationOption, pk=pk)

    def get(self, request, pk):
        option = self.get_object(pk)
        serializer = CustomizationOptionSerializer(option)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        option = self.get_object(pk)
        serializer = CustomizationOptionSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        option = self.get_object(pk)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RestaurantMenuAPIView(APIView):
    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        categories = MenuCategory.objects.filter(restaurant=restaurant)
        data = []

        for category in categories:
            items = MenuItem.objects.filter(category=category)
            category_data = {
                "category_name": category.name,
                "category_description": category.description,
                "items": []
            }

            for item in items:
                # Fetch customization groups and options if the item is customizable
                customizations = []
                if item.customizable:
                    groups = CustomizationGroup.objects.filter(menu_item=item)
                    for group in groups:
                        options = CustomizationOption.objects.filter(group=group)
                        customizations.append({
                            "group_name": group.name,
                            "options_allowed": group.options_allowed,
                            "options": [{"name": option.name, "price": option.price, "food_type": option.food_type} for option in options]
                        })

                # Append each menu item
                category_data["items"].append({
                    "name": item.name,
                    "price": item.price,
                    "photo_url": item.photo_url,
                    "customizable": item.customizable,
                    "customizations": customizations,
                    "food_type": item.food_type
                })

            data.append(category_data)

        return Response({
            "restaurant": restaurant.name,
            "menu": data
        }, status=status.HTTP_200_OK)

    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantOrdersAPIView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        restaurant = self.request.user.restaurant  # Assuming Restaurant is linked to User
        return Order.objects.filter(restaurant=restaurant).order_by('-created_at')