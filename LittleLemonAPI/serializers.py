from django.contrib.auth.models import User
from rest_framework import serializers

from LittleLemonAPI.models import MenuItem, Cart, Order, OrderItem


class UserMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "username"]

    def validate_username(self, value):
        # Ensure the user exists
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("No user found matching username.")
        return value


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'inventory', 'category']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menu_items', 'quantity', 'unit_price', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    # order_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'delivery_crew', 'status', 'total', 'date', 'order_items']
