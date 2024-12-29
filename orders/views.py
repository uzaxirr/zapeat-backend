from django.shortcuts import get_object_or_404

from authentication.models import Customer
from orders.models import Order
from authentication.serializers import User
from orders.serializers import OrderSerializer
from restaurants.models import Restaurant
from zapeat.std_utils import CustomAPIModule
from rest_framework.views import APIView


class RestaurantOrderView(APIView, CustomAPIModule):
    model = Order
    serializer_class = OrderSerializer

    def get_restaurant(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        return get_object_or_404(Restaurant, id=restaurant_id)

    def get(self, request, *args, **kwargs):
        """
        Get all orders for a given restaurant
        """
        restaurant = self.get_restaurant()
        all_orders = self.model.objects.filter(restaurant_id=restaurant.id)
        serialized_orders = OrderSerializer(all_orders, many=True)
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