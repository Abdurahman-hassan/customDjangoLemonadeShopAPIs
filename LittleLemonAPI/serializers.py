from django.contrib.auth.models import User
from rest_framework import serializers


class UserMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ["username"]

    def validate_username(self, value):
        # Ensure the user exists
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("No user found matching username.")
        return value
