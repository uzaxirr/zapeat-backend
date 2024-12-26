from rest_framework import serializers

from restaurants.serializers import CustomizationOptionSerializer
from .models import Order, OrderItem
from restaurants.models import CustomizationOption, MenuItem


class OrderItemSerializer(serializers.ModelSerializer):
    customizations = CustomizationOptionSerializer()
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'price', 'customizations']



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source="customer.mobile_number")
    restaurant_name = serializers.ReadOnlyField(source="restaurant.name")

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'restaurant', 'restaurant_name',
            'total_amount', 'payment_status', 'order_status', 'restaurant_status',
            'special_instructions', 'created_at', 'updated_at', 'items', 'order_items'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            customizations = item_data.pop('customizations', None)
            customizations_obj = CustomizationOption.objects.get(id=customizations)
            OrderItem.objects.create(order=order, customizations=customizations_obj, **item_data)
        
        return order
