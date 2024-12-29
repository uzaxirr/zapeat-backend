from django.shortcuts import get_object_or_404
from authentication.models import Customer
from orders.models import Order
from orders.serializers import OrderSerializer
from restaurants.models import Restaurant
from zapeat.std_utils import CustomAPIModule, StandardResultsSetPagination
from rest_framework.views import APIView


class RestaurantOrderView(APIView, CustomAPIModule):
    model = Order
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get_restaurant(self):
            restaurant_id = self.kwargs.get('restaurant_id')
            return get_object_or_404(Restaurant, id=restaurant_id)

    def get(self, request, *args, **kwargs):
        """
        Get all orders for a given restaurant
        """
        paginator = self.pagination_class()
        restaurant = self.get_restaurant()
        all_orders = self.model.objects.filter(restaurant_id=restaurant.id).order_by('-created_at')
        result_page = paginator.paginate_queryset(all_orders, request)
        serialized_orders = OrderSerializer(result_page, many=True)
        return self.success_response(data=serialized_orders.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new order for a given restaurant
        """
        restaurant = self.get_restaurant()
        serializer = OrderSerializer(data=request.data)
        user_dummy = Customer.objects.get(id=2) #TODO: Make user dynamic
        self.request.user = user_dummy
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user, restaurant=restaurant)
        return self.success_response(data=serializer.data, message="Order created successfully")

class DashboardOrdersView(APIView, CustomAPIModule):
    model = Order
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        """
        Get all orders for a given restaurant
        """
        paginator = self.pagination_class()
        all_orders = self.model.objects.all().order_by('-created_at')
        result_page = paginator.paginate_queryset(all_orders, request)
        serialized_orders = OrderSerializer(result_page, many=True)

        return paginator.get_paginated_response(serialized_orders.data)
