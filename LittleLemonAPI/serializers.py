from django.contrib.auth.models import User
from rest_framework import serializers

from LittleLemonAPI.models import MenuItem


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
