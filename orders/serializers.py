from rest_framework import serializers

from orders.models import Order, OrderItem
from restaurants.models import MenuItem

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'items', 'total_amount', 'status', 'created_at']
        read_only_fields = ['customer', 'total_amount', 'status', 'created_at']

    def validate(self, data):
        # Ensure only customers can place orders
        user = self.context['request'].user
        if not user.is_customer():
            raise serializers.ValidationError("Only customers can place orders.")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context['request']
        customer = self.context['request'].user.customer  # Assuming Customer is linked to User
        restaurant = validated_data['restaurant']

        # Ensure the restaurant exists and the owner is valid
        if not restaurant.owner == request.user:
            raise serializers.ValidationError("You can only place orders at valid restaurants.")


        # Create the order
        order = Order.objects.create(customer=customer, restaurant=restaurant, status='PENDING')

        total_amount = 0
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            price = menu_item.price * quantity

            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity, price=menu_item.price)
            total_amount += price

        # Update the order's total amount
        order.total_amount = total_amount
        order.save()

        return order
