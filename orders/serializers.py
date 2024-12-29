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
        menu_item = attrs.get('menu_item')
        quantity = attrs.get('quantity')
        customizations = attrs.get('customizations')
        
        # Calculate base price from menu item and quantity
        total_price = menu_item.price * quantity
        
        # Add customization price if any
        if customizations:
            total_price += customizations.price * quantity
            
        # Add calculated price to validated data
        attrs['price'] = total_price
        return attrs


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
        total_order_price = 0

        for item_data in items_data:
            #TODO: fix price calculation
            item_price = 0
            customizations = item_data.pop('customizations', None)
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            # Calculate item price
            item_price = menu_item.price * quantity

            # Add customization price if any
            if customizations:
                item_price += customizations.price * quantity

            # Add to total order price
            total_order_price += item_price

            # Create order item
            item_data.pop('price', None)  # Remove price if exists
            OrderItem.objects.create(
                order=order,
                customizations=customizations,
                price=item_price,
                **item_data
        )

        # Update order with total amount
        order.total_amount = total_order_price
        order.save()
        return order

    # def create(self, validated_data):
    #     items_data = validated_data.pop('items')
    #     # import pdb; pdb.set_trace()
    #     order = Order.objects.create(**validated_data)
    #     order_price = 0
    #
    #     for item_data in items_data:
    #         item_price = 0
    #         customizations = item_data.pop('customizations', None)
    #         menu_item = item_data['menu_item']
    #         if menu_item:
    #             item_price += menu_item.price * item_data['quantity']
    #         if customizations:
    #             total_price = item_price + customizations.price
    #         item_data.pop('price')
    #         OrderItem.objects.create(order=order, customizations=customizations, price=item_price, **item_data)
    #     order.total_amount = total_price
    #     import pdb; pdb.set_trace()
    #     return order
