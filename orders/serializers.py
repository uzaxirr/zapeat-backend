from rest_framework import serializers

from restaurants.serializers import CustomizationOptionSerializer
from .models import Order, OrderItem
from restaurants.models import CustomizationOption, MenuItem, Restaurant


class OrderItemSerializer(serializers.ModelSerializer):
    customizations = serializers.PrimaryKeyRelatedField(queryset=CustomizationOption.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['uuid', 'menu_item', 'quantity', 'price', 'customizations']

    def validate(self, attrs):
        import pdb; pdb.set_trace()
        pass



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source="customer.mobile_number")
    restaurant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'restaurant',
            'total_amount', 'payment_status', 'order_status', 'restaurant_status',
            'special_instructions', 'created_at', 'updated_at', 'items', 'order_items'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at', 'price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in items_data:
            customizations = item_data.pop('customizations', None)
            menu_item = item_data['menu_item']
            if menu_item:
                total_price += menu_item.price * item_data['quantity']
            if customizations:
                total_price = total_price + customizations.price
            item_data.pop('price')
            OrderItem.objects.create(order=order, customizations=customizations, price=total_price, **item_data)
        
        return order
