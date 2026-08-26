from rest_framework import serializers
from .models import *
import random

import secrets


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Register
        fields = ["id", "name", "phone", "otp", "user_token"]
        read_only_fields = ["id", "otp"]

    def create(self, validated_data):

        otp = str(random.randint(1000, 9999))

        user_token = secrets.token_hex(32)

        user = Register.objects.create(
            name=validated_data["name"],
            phone=validated_data["phone"],
            otp=otp,
            user_token=user_token,
        )

        return user



from rest_framework import serializers
from .models import Register, Login
import random


class LoginSerializer(serializers.ModelSerializer):

    user_token = serializers.CharField(
        source="user.user_token",
        read_only=True
    )

    class Meta:
        model = Login
        fields = [
            "id",
            "phone",
            "otp",
            "created_at",
            "user_token"
        ]

        read_only_fields = [
            "id",
            "otp",
            "created_at",
            "user_token"
        ]

    def create(self, validated_data):

        phone = validated_data["phone"]

        # Find registered user
        try:
            register_user = Register.objects.get(phone=phone)

        except Register.DoesNotExist:
            raise serializers.ValidationError({
                "phone": "Phone number is not registered"
            })

        # Generate 4 digit OTP
        otp = str(random.randint(1000, 9999))

        # Create login and connect to Register
        login = Login.objects.create(
            user=register_user,
            phone=phone,
            otp=otp
        )

        return login