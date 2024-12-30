import boto3
from django.conf import settings
from django.http import Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from botocore.exceptions import ClientError

from authentication.permissions import IsRestaurantAdmin
from zapeat.std_utils import CustomAPIModule
from .models import (
    Restaurant,
    MenuCategory,
    MenuItem,
    CustomizationGroup,
    CustomizationOption
)
from .serializers import (
    RestaurantSerializer,
)
from orders.models import Order
from orders.serializers import OrderSerializer
from drf_yasg.utils import swagger_auto_schema

class RestaurantListView(APIView, CustomAPIModule):
    # permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: RestaurantSerializer(many=True)
        }
    )
    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return self.success_response(data=serializer.data, message="Restaurants fetched successfully", status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=RestaurantSerializer,
        responses={
            201: RestaurantSerializer,
            400: 'Invalid request'
        }
    )
    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(data=serializer.data, message="Restaurant created successfully", status_code=status.HTTP_201_CREATED)
        return self.validation_error_response(errors=serializer.errors, message="Invalid restaurant data")

class RestaurantDetailView(APIView, CustomAPIModule):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            restaurant = get_object_or_404(Restaurant, pk=pk)
            serializer = RestaurantSerializer(restaurant)
            return self.success_response(
                data=serializer.data,
                message="Restaurant details retrieved successfully"
            )
        except Http404:
            return self.not_found_response(
                message=f"Restaurant with id {pk} not found"
            )
        except Exception as e:
            return self.error_response(
                message="Failed to retrieve restaurant details",
                errors={"detail": str(e)}
            )

    def put(self, request, pk):
        try:
            restaurant = get_object_or_404(Restaurant, pk=pk)
            serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)

            if not serializer.is_valid():
                return self.validation_error_response(
                    errors=serializer.errors,
                    message="Invalid restaurant data"
                )

            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Restaurant updated successfully"
            )
        except Http404:
            return self.not_found_response(
                message=f"Restaurant with id {pk} not found"
            )
        except Exception as e:
            return self.error_response(
                message="Failed to update restaurant",
                errors={"detail": str(e)}
            )

    def delete(self, request, pk):
        try:
            restaurant = get_object_or_404(Restaurant, pk=pk)
            #delete all staff members associated with this restaurant
            restaurant.staff_members.all().delete()
            #delete all bank accounts associated with this restaurant
            bank_accounts = restaurant.bank_accounts.all()
            bank_accounts.delete()
            #delete the restaurant
            restaurant.delete()

            return self.success_response(
                message="Restaurant and associated data deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Http404:
            return self.not_found_response(
                message=f"Restaurant with id {pk} not found"
            )
        except Exception as e:
            return self.error_response(
                message="Failed to delete restaurant",
                errors={"detail": str(e)}
            )

class S3PreSignedUrlView(APIView, CustomAPIModule):
    # permission_classes = [permissions.IsAuthenticated]

    def generate_presigned_url(self, bucket_name, object_name, expiration=3600):
        """
        Generate a pre-signed URL for S3 to allow uploading an object.
        """
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.CIVO_BUCKET_ACCESS_KEY,
            aws_secret_access_key=settings.CIVO_BUCKET_SECRET_KEY,
            endpoint_url=f'https://{settings.CIVO_REGION}.object.civo.com'
        )
        try:
            response = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response, None
        except ClientError as e:
            return None, str(e)

    def post(self, request):
        body = request.data
        try:
            bucket_name = 'zapeat'
            object_key = f"restaurant_logos/{body['path']}"
            expiration_time = 3600  # URL validity time in seconds

            # Generate the pre-signed URL
            presigned_url, error = self.generate_presigned_url(
                bucket_name,
                object_key,
                expiration_time
            )

            if error:
                return self.error_response(
                    message="Failed to generate pre-signed URL",
                    errors={"detail": str(error)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return self.success_response(
                data={"url": presigned_url},
                message="Pre-signed URL generated successfully"
            )

        except Exception as e:
            return self.error_response(
                message="Failed to process request",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RestaurantMenuAPIView(APIView, CustomAPIModule):
    # permission_classes = [IsAuthenticated, IsRestaurantAdmin]

    def get(self, request, pk):
        try:
            restaurant = get_object_or_404(Restaurant, pk=pk)
            categories = MenuCategory.objects.filter(restaurant=restaurant)
            data = []

            for category in categories:
                items = MenuItem.objects.filter(category=category)
                category_data = {
                    "name": category.name,
                    "description": category.description,
                    "menu_items": []
                }

                for item in items:
                    customizations = []
                    if item.customizable:
                        groups = CustomizationGroup.objects.filter(menu_item=item)
                        for group in groups:
                            options = CustomizationOption.objects.filter(group=group)
                            customizations.append({
                                "group_name": group.name,
                                "options": [{"name": option.name, "price": option.price, "food_type": option.food_type} for option in options]
                            })

                    category_data["menu_items"].append({
                        "name": item.name,
                        "price": item.price,
                        "photo_url": item.photo_url,
                        "customizable": item.customizable,
                        "customizations": customizations,
                        "food_type": item.food_type
                    })

                data.append(category_data)

            return self.success_response(
                data={
                    "restaurant": restaurant.name,
                    "menu": data
                },
                message="Restaurant menu retrieved successfully"
            )

        except Http404:
            return self.not_found_response(
                message=f"Restaurant with id {pk} not found"
            )
        except Exception as e:
            return self.error_response(
                message="Failed to retrieve restaurant menu",
                errors={"detail": str(e)}
            )

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: 'Invalid request',
            403: 'Permission denied'
        }
    )
    def post(self, request, pk):
        try:
            restaurant = get_object_or_404(Restaurant, pk=pk)
            menu_categories = request.data.get("menu", [])

            if not menu_categories:
                return self.validation_error_response(
                    errors={"menu_categories": ["Menu categories are required."]},
                    message="Missing required data"
                )
            
            # Delete all existing menu data for this restaurant
            MenuCategory.objects.filter(restaurant=restaurant).delete()

            # Process menu categories and items
            for category_data in menu_categories:
                category = MenuCategory.objects.get_or_create(
                    name=category_data["name"],
                    restaurant=restaurant,
                    defaults={"description": category_data.get("description", "")}
                )

                for item_data in category_data.get("menu_items", []):
                    menu_item = MenuItem.objects.create(
                        name=item_data["name"],
                        category=category[0] if isinstance(category, tuple) else category,
                        description = item_data.get("description", ""),
                        price = item_data["price"],
                        photo_url = item_data.get("photo_url", ""),
                        customizable = item_data.get("customizable", False),
                        food_type = item_data.get("food_type"),
                        spice_level = item_data.get("spice_level", 0),
                        sweetness_level = item_data.get("sweetness_level", 0),
                        must_try = item_data.get("must_try", False),

                    )

                    if item_data.get("customizable"):
                        for group_data in item_data.get("customization_groups", []):
                            group = CustomizationGroup.objects.get_or_create(
                                name=group_data["name"],
                                menu_item=menu_item,
                                defaults={
                                    "max_options_allowed": group_data.get("max_options_allowed", 1),
                                    "min_options_allowed": group_data.get("min_options_allowed", 0)
                                }
                            )

                            for option_data in group_data.get("options", []):
                                CustomizationOption.objects.create(
                                    name=option_data["name"],
                                    group=group[0] if isinstance(group, tuple) else group,
                                    price=option_data.get("price", 0.0),
                                    food_type=option_data.get("food_type"),
                                    spice_level=option_data.get("spice_level", 0),
                                    sweetness_level=option_data.get("sweetness_level", 0)
                                )
            # Fetch updated menu for response

            categories = MenuCategory.objects.filter(restaurant=restaurant)
            response_data = []


            for category in categories:
                items = MenuItem.objects.filter(category=category)
                category_data = {
                    "category_name": category.name,
                    "category_description": category.description,
                    "items": []
                }

                for item in items:
                    customizations = []

                    if item.customizable:
                        groups = CustomizationGroup.objects.filter(menu_item=item)
                        for group in groups:
                            options = CustomizationOption.objects.filter(group=group)
                            customizations.append({
                                "group_name": group.name,
                                "options": [{"name": option.name, "price": option.price, "food_type": option.food_type} for option in options]
                            })

                    category_data["items"].append({
                        "name": item.name,
                        "price": item.price,
                        "photo_url": item.photo_url,
                        "customizable": item.customizable,
                        "customizations": customizations,
                        "food_type": item.food_type
                    })

                response_data.append(category_data)

            return self.success_response(
                data={
                    "restaurant": restaurant.name,
                    "menu": response_data
                },
                message="Menu created/updated successfully",
                status_code=status.HTTP_201_CREATED
            )

        except Http404:
            return self.not_found_response(
                message=f"Restaurant with id {pk} not found"
            )
        except Exception as e:
            return self.error_response(
                message="Failed to create/update menu",
                errors={"detail": str(e)}
            )

class RestaurantOrdersAPIView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    @swagger_auto_schema(
        responses={
            200: OrderSerializer(many=True)
        }
    )
    def get_queryset(self):
        restaurant = self.request.user.restaurant  # Assuming Restaurant is linked to User
        return Order.objects.filter(restaurant=restaurant).order_by('-created_at')