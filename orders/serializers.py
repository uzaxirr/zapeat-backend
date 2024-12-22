from rest_framework import serializers
from .models import Order, OrderItem
from restaurants.models import MenuItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'price']
        extra_kwargs = {'order': {'required': False}}


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source="customer.mobile_number")
    restaurant_name = serializers.ReadOnlyField(source="restaurant.name")

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'restaurant', 'restaurant_name',
            'total_amount', 'payment_status', 'order_status',
            'special_instructions', 'created_at', 'updated_at', 'items', 'order_items'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']

    # def validate(self, data):
    #     items = data.get('items', [])
    #     calculated_total = sum(item['price'] * item['quantity'] for item in items)
    #     if abs(float(data['total_amount']) - calculated_total) > 0.01:
    #         raise serializers.ValidationError({
    #             "total_amount": f"Total amount ({data['total_amount']}) does not match sum of item prices ({calculated_total})"
    #         })
        
    #     restaurant = data['restaurant']
    #     for item in items:
    #         menu_item = item['menu_item']
    #         if menu_item.category.restaurant.id != restaurant.id:
    #             raise serializers.ValidationError({
    #                 "items": f"Menu item {menu_item.name} does not belong to the selected restaurant"
    #             })
        
    #     return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        import pdb; pdb.set_trace()
        order = Order.objects.create(**validated_data)
        
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                **item_data
            ) for item_data in items_data
        ])
        
        return order
