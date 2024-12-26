from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from authentication.serializers import User
from restaurants.models import Restaurant
from .models import Order, OrderItem
from rest_framework.permissions import AllowAny
from .serializers import OrderSerializer, OrderItemSerializer
from drf_yasg.utils import swagger_auto_schema


class RestaurantOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        return Order.objects.filter(
            restaurant_id=restaurant_id
        ).select_related(
            'customer',
            'restaurant'
        ).prefetch_related(
            'items',
            'items__menu_item',
            'items__customizations'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter by order status if provided
        order_status = request.query_params.get('status')
        if order_status:
            queryset = queryset.filter(order_status=order_status)

        restaurant_status = request.query_params.get('restaurant_status')
        if restaurant_status:
            queryset = queryset.filter(restaurant_status=restaurant_status)

        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date or end_date:
            if not start_date or not end_date:
                raise ValidationError("Both 'start_date' and 'end_date' must be provided.")
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        # Filter by customer name if provided
        customer_name = request.query_params.get('customer_name')
        if customer_name:
            queryset = queryset.filter(customer__name__icontains=customer_name)

        # Filter by specific item ID if provided
        item_id = request.query_params.get('item_id')
        if item_id:
            queryset = queryset.filter(items__menu_item__id=item_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# List/Create Orders
class OrderListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: 'Invalid request'
        }
    )
    def post(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Set a dummy user for testing purposes
        user_dummy = User.objects.get(id=6)
        self.request.user = user_dummy

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user, restaurant=restaurant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            200: OrderSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        return Order.objects.filter(restaurant_id=restaurant_id).select_related(
            'customer', 'restaurant'
        ).prefetch_related('items__customizations')


# Retrieve/Update/Delete a Single Order
class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Filter orders by restaurant if required
        restaurant_id = self.kwargs.get('restaurant_id')
        return Order.objects.filter(restaurant_id=restaurant_id)

    @swagger_auto_schema(
        responses={
            200: OrderSerializer,
            404: 'Order not found'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={
            200: OrderSerializer,
            400: 'Invalid request',
            404: 'Order not found'
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: 'Order deleted successfully',
            404: 'Order not found'
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# List/Create Order Items
class OrderItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Filter order items by a specific order
        order_id = self.kwargs.get('order_id')
        return OrderItem.objects.filter(order_id=order_id).prefetch_related('customizations')

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        serializer.save(order=order)


# Retrieve/Update/Delete a Single Order Item
class OrderItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Ensure the order item belongs to the specified order
        order_id = self.kwargs.get('order_id')
        return OrderItem.objects.filter(order_id=order_id)

    def perform_update(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        serializer.save(order=order)
