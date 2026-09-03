from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import *
from .models import *

from django.utils import timezone
from datetime import timedelta

from rest_framework.pagination import PageNumberPagination


@api_view(["POST","GET"])
def register_user(request):

    # =========================
    # POST - Register User
    # =========================
    if request.method == "POST":

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "Registration successful",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "phone": user.phone,
                    "otp": user.otp,
                    "email": user.email,
                    # "user_token": user.user_token,
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    # =========================
    # GET - Get All Users
    # =========================
    if request.method == "GET":

        users = Register.objects.all()

        serializer = UserSerializer(users, many=True)

        return Response({
            "message": "Users fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)




@api_view(["POST"])
def login_user(request):

    serializer = LoginSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user_type = serializer.validated_data["user_type"]

        otp = serializer.validated_data["otp"]

        # =================================================
        # ADMIN
        # =================================================

        if user_type == "admin":

            admin = serializer.validated_data["admin"]

            return Response({
                "message": "OTP generated successfully",
                "data": {
                    "name": admin.name,
                    "phone": admin.phone,
                    "otp": admin.otp,
                    "user_type": "admin"
                }
            }, status=status.HTTP_200_OK)

        # =================================================
        # NORMAL USER
        # =================================================

        user = serializer.validated_data["user"]

        return Response({
            "message": "OTP generated successfully",
            "data": {
                "name": user.name,
                "phone": user.phone,
                "otp": user.otp,
                "user_type": "user"
            }
        }, status=status.HTTP_200_OK)

    return Response({
        "message": "Login failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
def verify_otp(request):

    phone = request.data.get("phone")
    otp = request.data.get("otp")

    # =====================================================
    # CHECK PHONE
    # =====================================================

    if not phone:
        return Response({
            "message": "Phone number is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # CHECK OTP
    # =====================================================

    if not otp:
        return Response({
            "message": "OTP is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # FIRST CHECK ADMIN
    # =====================================================

    try:

        admin = Admin.objects.get(
            phone=phone
        )

        # Check OTP
        if admin.otp != otp:
            return Response({
                "message": "Invalid OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP expiry - 30 seconds
        if not admin.otp_created_at or \
           timezone.now() > admin.otp_created_at + timedelta(seconds=30):

            return Response({
                "message": "OTP expired. Please generate a new OTP."
            }, status=status.HTTP_400_BAD_REQUEST)

        # =================================================
        # OTP CORRECT → CLEAR OTP
        # =================================================

        admin.otp = None
        admin.otp_created_at = None

        admin.save(
            update_fields=[
                "otp",
                "otp_created_at"
            ]
        )

        # =================================================
        # ADMIN SUCCESS
        # =================================================

        return Response({
            "message": "OTP verified successfully",
            "data": {
                "name": admin.name,
                "phone": admin.phone,
                "user_token": admin.user_token,
                "user_type": "admin"
            }
        }, status=status.HTTP_200_OK)

    except Admin.DoesNotExist:

        pass

    # =====================================================
    # THEN CHECK NORMAL USER
    # =====================================================

    try:

        user = Register.objects.get(
            phone=phone
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Phone number is not registered"
        }, status=status.HTTP_404_NOT_FOUND)

    # =====================================================
    # CHECK USER OTP
    # =====================================================

    if user.otp != otp:

        return Response({
            "message": "Invalid OTP"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # CHECK OTP EXPIRY - 30 SECONDS
    # =====================================================

    # if not user.otp_created_at or \
    #    timezone.now() > user.otp_created_at + timedelta(seconds=30):

    #     return Response({
    #         "message": "OTP expired. Please generate a new OTP."
    #     }, status=status.HTTP_400_BAD_REQUEST)

    if not user.otp_created_at:
        return Response({
            "message": "OTP expired. Please generate a new OTP."
        }, status=status.HTTP_400_BAD_REQUEST)

    expiry_time = user.otp_created_at + timedelta(seconds=30)

    if timezone.now() > expiry_time:
        return Response({
            "message": "OTP expired. Please generate a new OTP."
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # OTP CORRECT → CLEAR OTP
    # =====================================================

    user.otp = None
    user.otp_created_at = None

    user.save(
        update_fields=[
            "otp",
            "otp_created_at"
        ]
    )

    # =====================================================
    # USER SUCCESS
    # =====================================================

    return Response({
        "message": "OTP verified successfully",
        "data": {
            "name": user.name,
            "phone": user.phone,
            "user_token": user.user_token,
            "user_type": "user"
        }
    }, status=status.HTTP_200_OK)



# =========================================================
# LOGOUT USER
# =========================================================

@api_view(["POST"])
def logout_user(request):

    # user_token = request.data.get("user_token")

    user_token = request.headers.get("user-token")

    # Check user_token is provided
    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check user_token exists
    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "message": "Logout successful"
    }, status=status.HTTP_200_OK)


# =========================================================
# PROFILE
# =========================================================

@api_view(["GET", "PUT"])
def profile(request):

    user_token = request.headers.get("user-token")


    # Check user_token
    if not user_token:

        return Response({
            "message": "user_token is required in header"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Find user
    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # =========================
    # GET PROFILE
    # =========================

    if request.method == "GET":

        return Response({
            "message": "Profile fetched successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "user_token": user.user_token,
            }
        }, status=status.HTTP_200_OK)

    # =========================
    # UPDATE PROFILE
    # =========================

    if request.method == "PUT":

        name = request.data.get("name")
        # phone = request.data.get("phone")
        email = request.data.get("email")

        if name:
            user.name = name

        if email:
            user.email = email

        user.save()

        return Response({
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "email": user.email,
                "user_token": user.user_token,
            }
        }, status=status.HTTP_200_OK)
    


@api_view(["GET", "POST"])
def save_address(request):

    user_token = request.headers.get("user-token")

    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # FIND USER
    # =====================================================

    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # =====================================================
    # POST - SAVE ADDRESS
    # =====================================================

    if request.method == "POST":

        # Copy request data
        data = request.data.copy()

        # Remove user_token if sent in body
        data.pop("user_token", None)

        # Validate address
        serializer = AddressSerializer(
            data=data
        )

        if serializer.is_valid():

            address = serializer.save(
                user=user
            )

            return Response({

                "message": "Address saved successfully",

                "data": AddressSerializer(
                    address
                ).data

            }, status=status.HTTP_201_CREATED)

        return Response({

            "message": "Address save failed",

            "errors": serializer.errors

        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # GET - ADDRESS HISTORY WITH PAGINATION
    # =====================================================

    if request.method == "GET":

        # =================================================
        # GET COUNT
        # =================================================

        count = request.query_params.get(
            "count",
            5
        )

        try:

            count = int(count)

        except ValueError:

            return Response({
                "message": "count must be a number"
            }, status=status.HTTP_400_BAD_REQUEST)

        if count <= 0:

            return Response({
                "message": "count must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)

        # =================================================
        # GET USER ADDRESSES
        # =================================================

        addresses = Address.objects.filter(
            user=user
        ).order_by(
            "-id"
        )

        # =================================================
        # PAGINATION
        # =================================================

        paginator = PageNumberPagination()
        paginator.page_size = count
        result_page = paginator.paginate_queryset(addresses,request)

        # =================================================
        # SERIALIZE
        # =================================================

        serializer = AddressSerializer(result_page,many=True)

        # =================================================
        # PAGINATION DETAILS
        # =================================================

        current_page = paginator.page.number
        total_pages = paginator.page.paginator.num_pages
        total_items = paginator.page.paginator.count

        # Previous page
        if paginator.page.has_previous():

            previous_page = paginator.page.previous_page_number()

        else:

            previous_page = None

        # Next page
        if paginator.page.has_next():

            next_page = paginator.page.next_page_number()

        else:

            next_page = None

        # =================================================
        # RESPONSE
        # =================================================

        return Response({

            "message": "Address history fetched successfully",

            "pagination": {
                "page": current_page,
                "count": count,
                "total_items": total_items,
                "total_pages": total_pages,
                "previous_page": previous_page,
                "next_page": next_page
            },

            "data": serializer.data

        }, status=status.HTTP_200_OK)



@api_view(["DELETE"])
def delete_address(request, address_id):

    # Get user token from header
    user_token = request.headers.get("user-token")

    if not user_token:
        return Response({
            "message": "user_token is required in header"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Find user
    try:
        user = Register.objects.get(
            user_token=user_token
        )
    except Register.DoesNotExist:
        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Find address belonging to this user
    try:
        address = Address.objects.get(
            id=address_id,
            user=user
        )
    except Address.DoesNotExist:
        return Response({
            "message": "Address not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Delete address
    address.delete()

    return Response({
        "message": "Address deleted successfully",
        "address_id": address_id
    }, status=status.HTTP_200_OK)


# =========================================================
# ADMIN LOGIN - GENERATE OTP
# =========================================================

@api_view(["POST"])
def admin_login(request):

    serializer = LoginSerializer(
        data=request.data
    )

    if serializer.is_valid():

        admin = serializer.validated_data["admin"]
        otp = serializer.validated_data["otp"]

        return Response({
            "message": "Admin OTP generated successfully",
            "data": {
                "name": admin.name,
                "phone": admin.phone,
                "otp": otp
            }
        }, status=status.HTTP_200_OK)

    return Response({
        "message": "Admin login failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def order_history(request):

    user_token = request.headers.get("user-token")

    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # FIND USER
    # =====================================================

    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # =====================================================
    # GET COUNT
    # =====================================================

    count = request.query_params.get("count", 5)

    try:

        count = int(count)

    except ValueError:

        return Response({
            "message": "count must be a number"
        }, status=status.HTTP_400_BAD_REQUEST)

    if count <= 0:

        return Response({
            "message": "count must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)

    # =====================================================
    # GET ORDERS
    # =====================================================

    orders = Order.objects.filter(
        user=user
    ).select_related(
        "user",
        "address"
    ).prefetch_related(
        "items"
    ).order_by(
        "-created_at"
    )

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = PageNumberPagination()
    paginator.page_size = count
    result_page = paginator.paginate_queryset(orders,request)

    # =====================================================
    # SERIALIZE
    # =====================================================

    serializer = OrderSerializer(
        result_page,
        many=True
    )

    # =====================================================
    # PAGINATION DETAILS
    # =====================================================

    current_page = paginator.page.number
    total_pages = paginator.page.paginator.num_pages
    total_items = paginator.page.paginator.count

    if paginator.page.has_previous():

        previous_page = paginator.page.previous_page_number()

    else:

        previous_page = None

    if paginator.page.has_next():

        next_page = paginator.page.next_page_number()

    else:

        next_page = None

    # =====================================================
    # RESPONSE
    # =====================================================

    return Response({

        "message": "Order history fetched successfully",

        "pagination": {
            "page": current_page,
            "count": count,
            "total_items": total_items,
            "total_pages": total_pages,
            "previous_page": previous_page,
            "next_page": next_page
        },

        "data": serializer.data

    }, status=status.HTTP_200_OK)


# ----------------------------------- PRESCRIPTION ------------------------------------------

from django.core.paginator import Paginator, EmptyPage



# ============================================================
# PRESCRIPTION - GET
# GET /api/prescription/?page=1&count=3
# ============================================================

@api_view(["GET"])
def prescription_get_api(request):

    prescriptions = prescription.objects.all().order_by("-id")

    # ========================================================
    # PAGE AND COUNT
    # ========================================================

    try:
        page = int(request.GET.get("page", 1))
        count = int(request.GET.get("count", 3))

        if page < 1:
            page = 1

        if count < 1:
            count = 3

    except (ValueError, TypeError):

        page = 1
        count = 3

    # ========================================================
    # PAGINATION
    # ========================================================

    paginator = Paginator(
        prescriptions,
        count
    )

    total_data = paginator.count
    total_pages = paginator.num_pages

    try:

        result_page = paginator.page(page)

    except EmptyPage:

        return Response(
            {
                "status": False,
                "message": "Page not found",
                "page": page,
                "count": count,
                "total_data": total_data,
                "total_pages": total_pages,
                "data": []
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # ========================================================
    # SERIALIZER
    # ========================================================

    serializer = PrescriptionSerializer(
    result_page.object_list,
    many=True
)

    # ========================================================
    # RESPONSE
    # ========================================================

    return Response(
        {
            "status": True,
            "message": "Prescription list fetched successfully",
            "page": page,
            "count": count,
            "total_data": total_data,
            "total_pages": total_pages,
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )
# ============================================================
# PRESCRIPTION - POST
# POST /api/prescription/create/
# ============================================================

@api_view(["POST"])
def prescription_post_api(request):

    serializer = PrescriptionSerializer(
        data=request.data
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "status": True,
                "message": "Prescription created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # ========================================================
    # VALIDATION ERROR
    # ========================================================

    return Response(
        {
            "status": False,
            "message": "Validation error",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# GLASS PRODUCT - GET
# GET /api/glass-product/?page=1&count=3
# ============================================================

@api_view(["GET"])
def glass_product_get_api(request):

    products = glass_product.objects.all().order_by("-id")

    # ========================================================
    # PAGE AND COUNT
    # ========================================================

    try:

        page = int(request.GET.get("page", 1))
        count = int(request.GET.get("count", 3))

        if page < 1:
            page = 1

        if count < 1:
            count = 3

    except (ValueError, TypeError):

        page = 1
        count = 3

    # ========================================================
    # PAGINATION
    # ========================================================

    paginator = Paginator(
        products,
        count
    )

    total_data = paginator.count
    total_pages = paginator.num_pages

    try:

        result_page = paginator.page(page)

    except EmptyPage:

        return Response(
            {
                "status": False,
                "message": "Page not found",
                "page": page,
                "count": count,
                "total_data": total_data,
                "total_pages": total_pages,
                "data": []
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # ========================================================
    # SERIALIZER
    # ========================================================

    serializer = GlassProductSerializer(
        result_page,
        many=True
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return Response(
        {
            "status": True,
            "message": "Glass products fetched successfully",
            "page": page,
            "count": count,
            "total_data": total_data,
            "total_pages": total_pages,
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# GLASS PRODUCT - POST
# POST /api/glass-product/create/
# ============================================================

@api_view(["POST"])
def glass_product_post_api(request):

    serializer = GlassProductSerializer(
        data=request.data
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "status": True,
                "message": "Glass product created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # ========================================================
    # VALIDATION ERROR
    # ========================================================

    return Response(
        {
            "status": False,
            "message": "Validation error",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# ------------------------------------------------------------------------------------------


@api_view(["GET", "POST", "DELETE"])
def add_wishlist(request):

    user_token = request.headers.get("user-token")

    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)


    # FIND USER
    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)


    # POST - ADD PRODUCT TO WISHLIST
    if request.method == "POST":

        # GET PRODUCT ID
        product_id = request.data.get("product_id")

        if not product_id:

            return Response({
                "message": "product_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)


        # FIND PRODUCT
        try:

            product = glass_product.objects.get(
                id=product_id
            )

        except glass_product.DoesNotExist:

            return Response({
                "message": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)


        # CHECK ALREADY IN WISHLIST

        wishlist_item = Wishlist.objects.filter(
            user=user,
            product=product
        ).first()

        if wishlist_item:

            return Response({

                "message": "Product already exists in wishlist",

                # "data": GlassProductSerializer(
                #     product
                # ).data

            }, status=status.HTTP_200_OK)


        # CREATE WISHLIST

        Wishlist.objects.create(
            user=user,
            product=product
        )


        # RESPONSE

        return Response({

            "message": "Product added to wishlist successfully",

            "data": GlassProductSerializer(
                product
            ).data

        }, status=status.HTTP_201_CREATED)

    # =====================================================
    # GET - WISHLIST WITH PAGINATION
    # =====================================================

    if request.method == "GET":


        # GET COUNT

        count = request.query_params.get(
            "count",
            10
        )

        try:

            count = int(count)

        except ValueError:

            return Response({
                "message": "count must be a number"
            }, status=status.HTTP_400_BAD_REQUEST)

        if count <= 0:

            return Response({
                "message": "count must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)


        # GET USER WISHLIST

        wishlist = Wishlist.objects.filter(
            user=user
        ).select_related(
            "product"
        ).order_by(
            "-created_at"
        )


        # PAGINATION

        paginator = PageNumberPagination()
        paginator.page_size = count
        result_page = paginator.paginate_queryset(wishlist,request)


        # GET PRODUCT DETAILS

        data = []

        for item in result_page:

            data.append(
                GlassProductSerializer(
                    item.product
                ).data
            )


        # PAGINATION DETAILS

        current_page = paginator.page.number
        total_pages = paginator.page.paginator.num_pages
        total_items = paginator.page.paginator.count


        # PREVIOUS PAGE

        if paginator.page.has_previous():

            previous_page = (
                paginator.page.previous_page_number()
            )

        else:

            previous_page = None


        # NEXT PAGE

        if paginator.page.has_next():

            next_page = (
                paginator.page.next_page_number()
            )

        else:

            next_page = None


        # RESPONSE

        return Response({

            "message": "Wishlist fetched successfully",
            "pagination": {
                "page": current_page,
                "count": count,
                "total_items": total_items,
                "total_pages": total_pages,
                "previous_page": previous_page,
                "next_page": next_page
            },
            "data": data

        }, status=status.HTTP_200_OK)


    # DELETE - REMOVE PRODUCT FROM WISHLIST

    if request.method == "DELETE":

        # GET PRODUCT ID
        product_id = request.data.get("product_id")

        if not product_id:

            return Response({

                "message": "product_id is required"

            }, status=status.HTTP_400_BAD_REQUEST)


        # FIND WISHLIST ITEM
        try :

            wishlist_item = Wishlist.objects.get(
                user=user,
                product_id=product_id
            )

        except Wishlist.DoesNotExist:

            return Response({

                "message": "Product not found in wishlist"

            }, status=status.HTTP_404_NOT_FOUND)


        # DELETE
        wishlist_item.delete()

        return Response({

            "message": "Product removed from wishlist successfully",
            "data": GlassProductSerializer(product).data

        }, status=status.HTTP_200_OK)



@api_view(["GET"])
def eyeglasses(request):

    user_token = request.headers.get("user-token")

    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)


    # =====================================================
    # FIND USER
    # =====================================================

    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    count = request.query_params.get(
        "count",
        9
    )

    try:

        count = int(count)

    except ValueError:

        return Response({
            "message": "count must be a number"
        }, status=status.HTTP_400_BAD_REQUEST)


    if count <= 0:

        return Response({
            "message": "count must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)


    # =====================================================
    # GET EYEGLASSES
    # =====================================================

    products = glass_product.objects.filter(
        category_type="eyeglasses"
    ).order_by(
        "-created_at"
    )


    # PAGINATION

    paginator = PageNumberPagination()
    paginator.page_size = count
    result_page = paginator.paginate_queryset(products,request)

    # RESPONSE DATA

    serializer = GlassProductSerializer(
        result_page,
        many=True,
        context={
            "user": user
        }
    )

    data = serializer.data

    # PAGINATION DETAILS

    current_page = paginator.page.number
    total_pages = paginator.page.paginator.num_pages
    total_items = paginator.page.paginator.count


    # PREVIOUS PAGE

    if paginator.page.has_previous():

        previous_page = (
            paginator.page.previous_page_number()
        )

    else:

        previous_page = None

    # NEXT PAGE

    if paginator.page.has_next():

        next_page = (
            paginator.page.next_page_number()
        )

    else:

        next_page = None

    return Response({

        "message": "Eyeglasses fetched successfully",
        "pagination": {
            "page": current_page,
            "count": count,
            "total_items": total_items,
            "total_pages": total_pages,
            "previous_page": previous_page,
            "next_page": next_page
        },
        "data": data

    }, status=status.HTTP_200_OK)



@api_view(["GET"])
def sunglasses(request):

    user_token = request.headers.get("user-token")

    if not user_token:

        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # FIND USER
    try:

        user = Register.objects.get(
            user_token=user_token
        )

    except Register.DoesNotExist:

        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)


    # GET COUNT

    count = request.query_params.get(
        "count",
        9
    )

    try:

        count = int(count)

    except ValueError:

        return Response({
            "message": "count must be a number"
        }, status=status.HTTP_400_BAD_REQUEST)


    if count <= 0:

        return Response({
            "message": "count must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)

    # GET SUNGLASSES

    products = glass_product.objects.filter(
        category_type="sunglasses"
    ).order_by(
        "-created_at"
    )

    # PAGINATION

    paginator = PageNumberPagination()
    paginator.page_size = count
    result_page = paginator.paginate_queryset(products,request)

    # RESPONSE DATA
    serializer = GlassProductSerializer(
        result_page,
        many=True,
        context={
            "user": user
        }
    )

    data = serializer.data

    # PAGINATION DETAILS

    current_page = paginator.page.number
    total_pages = paginator.page.paginator.num_pages
    total_items = paginator.page.paginator.count

    # PREVIOUS PAGE
    
    if paginator.page.has_previous():

        previous_page = (
            paginator.page.previous_page_number()
        )

    else:

        previous_page = None

    # NEXT PAGE

    if paginator.page.has_next():

        next_page = (
            paginator.page.next_page_number()
        )

    else:

        next_page = None

    return Response({
        "message": "Sunglasses fetched successfully",
        "pagination": {
            "page": current_page,
            "count": count,
            "total_items": total_items,
            "total_pages": total_pages,
            "previous_page": previous_page,
            "next_page": next_page
        },
        "data": data
    }, status=status.HTTP_200_OK)



from django.db.models import Q


@api_view(["GET"])
def search_products(request):

    filter = request.query_params.get("filter")

    if not filter:

        return Response({
            "message": "search is required"
        }, status=status.HTTP_400_BAD_REQUEST)


    count = request.query_params.get(
        "count",
        10
    )

    try:

        count = int(count)

    except ValueError:

        return Response({
            "message": "count must be a number"
        }, status=status.HTTP_400_BAD_REQUEST)


    if count <= 0:

        return Response({
            "message": "count must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)


    # =====================================================
    # SEARCH PRODUCTS
    # =====================================================

    products = glass_product.objects.filter(
        Q(model_name__icontains=filter) |
        Q(category_type__icontains=filter)
        ).order_by(
            "-created_at"
        )


    paginator = PageNumberPagination()
    paginator.page_size = count
    result_page = paginator.paginate_queryset(products,request)

    # SERIALIZER

    serializer = GlassProductSerializer(
        result_page,
        many=True
    )


    # PAGINATION DETAILS

    current_page = paginator.page.number
    total_pages = paginator.page.paginator.num_pages
    total_items = paginator.page.paginator.count


    # PREVIOUS PAGE

    if paginator.page.has_previous():

        previous_page = (
            paginator.page.previous_page_number()
        )

    else:

        previous_page = None

    # NEXT PAGE

    if paginator.page.has_next():

        next_page = (
            paginator.page.next_page_number()
        )

    else:

        next_page = None

    return Response({
        "message": "Search results fetched successfully",
        "search": filter,
        "pagination": {
            "page": current_page,
            "count": count,
            "total_items": total_items,
            "total_pages": total_pages,
            "previous_page": previous_page,
            "next_page": next_page
        },
        "data": serializer.data

    }, status=status.HTTP_200_OK)

