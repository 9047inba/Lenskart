from rest_framework import serializers
from .models import *

import random
import secrets

from django.utils import timezone

# =========================================================
# REGISTER SERIALIZER
# =========================================================

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Register

        fields = [
            "id",
            "name",
            "phone",
            "otp",
            "email",
            "user_token",
        ]

        read_only_fields = [
            "id",
            "otp",
            "email",
            "user_token",
        ]

    def create(self, validated_data):

        otp = str(random.randint(1000, 9999))
        user_token = secrets.token_hex(32)
        user = Register.objects.create(
            name=validated_data["name"],
            phone=validated_data["phone"],
            otp=otp,
            otp_created_at=timezone.now(),
            user_token=user_token,
        )

        return user


# =========================================================
# LOGIN SERIALIZER
# =========================================================

class LoginSerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=15)

    def validate(self, data):

        phone = data["phone"]

        # =================================================
        # FIRST CHECK ADMIN
        # =================================================

        try:

            admin = Admin.objects.get(
                phone=phone
            )

            otp = str(random.randint(1000, 9999))

            admin.otp = otp
            admin.otp_created_at = timezone.now()

            admin.save(
                update_fields=["otp", "otp_created_at"]
            )

            data["admin"] = admin
            data["otp"] = otp
            data["user_type"] = "admin"

            return data

        except Admin.DoesNotExist:

            pass

        # =================================================
        # THEN CHECK NORMAL USER
        # =================================================

        try:

            user = Register.objects.get(
                phone=phone
            )

        except Register.DoesNotExist:

            raise serializers.ValidationError({
                "phone": "Phone number is not registered"
            })

        # Generate OTP
        otp = str(random.randint(1000, 9999))

        user.otp = otp
        user.otp_created_at = timezone.now()
        
        user.save(
            update_fields=["otp", "otp_created_at"]
        )

        data["user"] = user
        data["otp"] = otp
        data["user_type"] = "user"

        return data


# ADDRESS SERIALIZER

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ["id","full_name","phone","street_address","city","state","pincode","landmark","address_type","is_default","created_at",]
        read_only_fields = ["id","created_at",]


# ORDER ITEM SERIALIZER

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(read_only=True)
    color_frame = serializers.CharField(source="frame_color",read_only=True)
    price = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    review = serializers.CharField(read_only=True,allow_blank=True)

    class Meta:
        model = OrderItem

        fields = ["id","product_name","color_frame","price","date","review",]
        read_only_fields = ["id","product_name","color_frame","price","date","review",]

    def get_price(self, obj):

        return f"Rs. {obj.price}"

    def get_date(self, obj):

        if obj.date:
            return obj.date.strftime("%b %d, %Y")

        return ""


# ORDER SERIALIZER

class OrderSerializer(serializers.ModelSerializer):

    order_id = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    color_frame = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.name",read_only=True)
    mobile_number = serializers.CharField(source="user.phone",read_only=True)
    address = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = ["order_id","date","price","product_name","color_frame","address","review",

                    # User
                    "user_name","mobile_number",

                    # Order details
                    "order_status","payment_status",

                    # Optional
                    "items",  ]

        read_only_fields = ["order_id","date","price","product_name","color_frame",
                            "address","review","user_name","mobile_number",]

    # ORDER ID
    def get_order_id(self, obj):

        return f"OD{obj.id:08d}"

    # DATE
    def get_date(self, obj):

        if obj.created_at:
            return obj.created_at.strftime("%b %d, %Y")

        return ""

    # PRICE
    def get_price(self, obj):

        item = obj.items.first()

        if item:
            return f"Rs. {item.price}"

        return f"Rs. {obj.total_amount}"

    # PRODUCT NAME
    def get_product_name(self, obj):

        item = obj.items.first()

        if item:
            return item.product_name

        return ""

    # FRAME COLOR
    def get_color_frame(self, obj):

        item = obj.items.first()

        if item:
            return item.frame_color

        return ""

    # ADDRESS
    def get_address(self, obj):

        if not obj.address:
            return ""

        address = obj.address

        return {
            "full_name": address.full_name,
            "phone": address.phone,
            "street_address": address.street_address,
            "city": address.city,
            "state": address.state,
            "pincode": address.pincode,
            "landmark": address.landmark,
            "address_type": address.address_type,
        }

    # REVIEW
    def get_review(self, obj):

        item = obj.items.first()

        if item and item.review:
            return item.review

        return ""


# --------------------------------------PRESCRIPTION-------------------------------------------


class PrescriptionSerializer(serializers.ModelSerializer):

    class Meta:

        model = prescription

        fields = [
            "id",
            "name",
            "birth_year",

            "right_sph",
            "right_cyl",
            "right_axis",

            "left_sph",
            "left_cyl",
            "left_axis",

            "created_at"
        ]

        read_only_fields = [
            "id",
            "created_at"
        ]

# ============================================================
# GLASS PRODUCT SERIALIZER
# ============================================================

class GlassProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = glass_product

        fields = [
            "id",
            "product_name",
            "like",
            "category_type",
            "frame_size",
            "price",
            "rating",
            "structure_style",
            "target_audience",
            "collection_tier",
            "available_colors",
            "includes_adjustable_nose_pad",
            "applicable_for_buy_one_get_one",
            "created_at",
        ]
        search_fields = [
            "product_name",
            "category_type",
            "frame_size",
            "price",
            "color",
            "rating",
            "structure_style",
            "target_audience",
            "collection_tier",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


# --------------------------------------------------------------------------------------



class WishlistSerializer(serializers.ModelSerializer):

    product = GlassProductSerializer(read_only=True)

    class Meta:
        model = Wishlist

        fields = [
            "id",
            "product",
            "created_at",
        ]


# ============================================================
# CHECKOUT PRESCRIPTION RESPONSE SERIALIZER
# ============================================================

class CheckoutPrescriptionSerializer(serializers.ModelSerializer):

    right_eye = serializers.SerializerMethodField()
    left_eye = serializers.SerializerMethodField()

    class Meta:

        model = prescription

        fields = [
            "name",
            "birth_year",
            "right_eye",
            "left_eye",
        ]

    def get_right_eye(self, obj):

        return {
            "sph": str(obj.right_sph),
            "cyl": (
                str(obj.right_cyl)
                if obj.right_cyl is not None
                else None
            ),
            "axis": (
                str(obj.right_axis)
                if obj.right_axis is not None
                else None
            ),
        }

    def get_left_eye(self, obj):

        return {
            "sph": str(obj.left_sph),
            "cyl": (
                str(obj.left_cyl)
                if obj.left_cyl is not None
                else None
            ),
            "axis": (
                str(obj.left_axis)
                if obj.left_axis is not None
                else None
            ),
        }


# ============================================================
# CHECKOUT PRESCRIPTION INPUT SERIALIZER
# ============================================================

class CheckoutPrescriptionInputSerializer(serializers.Serializer):

    name = serializers.CharField(required=True)

    birth_year = serializers.IntegerField(required=True)

    right_eye = serializers.DictField(required=True)

    left_eye = serializers.DictField(required=True)

    def validate_right_eye(self, value):

        if "sph" not in value:

            raise serializers.ValidationError(
                "right_eye.sph is required."
            )

        return value

    def validate_left_eye(self, value):

        if "sph" not in value:

            raise serializers.ValidationError(
                "left_eye.sph is required."
            )

        return value


# ============================================================
# SELECT LENS SERIALIZER
# ============================================================

class SelectLensSerializer(serializers.ModelSerializer):

    lenstype = serializers.CharField(source="lens_type",required=True)
    lenspackage = serializers.CharField(source="lens_package",required=True)
    checkoutprescription = CheckoutPrescriptionInputSerializer(source="checkout_prescription",required=True)

    class Meta:

        model = SelectLens
        fields = [
            "id",
            "lenstype",
            "lenspackage",
            "checkoutprescription",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):

        prescription_data = validated_data.pop("checkout_prescription")
        right_eye = prescription_data.pop("right_eye")
        left_eye = prescription_data.pop("left_eye")
        prescription_obj = prescription.objects.create(
            name=prescription_data["name"],
            birth_year=prescription_data["birth_year"],
            # RIGHT EYE
            right_sph=right_eye["sph"],
            right_cyl=right_eye.get("cyl"),
            right_axis=right_eye.get("axis"),
            # LEFT EYE
            left_sph=left_eye["sph"],
            left_cyl=left_eye.get("cyl"),
            left_axis=left_eye.get("axis"),
        )
        select_lens = SelectLens.objects.create(
            checkout_prescription=prescription_obj,
            **validated_data
        )

        return select_lens


# ============================================================
# CHECKOUT SERIALIZER
# ============================================================

class CheckoutSerializer(serializers.Serializer):

    contact_information = serializers.DictField(required=True)
    shipping_address = serializers.DictField(required=True)

    def validate(self, data):

        contact = data["contact_information"]
        address = data["shipping_address"]

        # Contact information
        required_contact_fields = [
            "first_name",
            "last_name",
            "email",
            "phone"
        ]

        for field in required_contact_fields:
            if field not in contact:
                raise serializers.ValidationError({
                    "contact_information": {
                        field: "This field is required."
                    }
                })

        # Shipping address
        required_address_fields = [
            "street_address",
            "city",
            "state",
            "pincode"
        ]

        for field in required_address_fields:
            if field not in address:
                raise serializers.ValidationError({
                    "shipping_address": {
                        field: "This field is required."
                    }
                })

        return data



