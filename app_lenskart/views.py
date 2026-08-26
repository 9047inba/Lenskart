from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import *
from .models import *


@api_view(["POST"])
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
                    "user_token": user.user_token,
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    # =========================
    # GET - Get All Users
    # =========================
    # if request.method == "GET":

    #     users = Register.objects.all()

    #     serializer = UserSerializer(users, many=True)

    #     return Response({
    #         "message": "Users fetched successfully",
    #         "data": serializer.data
    #     }, status=status.HTTP_200_OK)



@api_view(["POST"])
def login_user(request):

    # =========================
    # POST - Login
    # =========================
    if request.method == "POST":

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            login = serializer.save()

            return Response({
                "message": "OTP generated successfully",
                "data": {
                    "id": login.id,
                    "phone": login.phone,
                    "otp": login.otp,
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Login failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    # =========================
    # GET - Get Login Details
    # =========================
    # if request.method == "GET":

    #     logins = Login.objects.all()

    #     serializer = LoginSerializer(logins, many=True)

    #     return Response({
    #         "message": "Login details fetched successfully",
    #         "data": serializer.data
    #     }, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout_user(request):

    user_token = request.data.get("user_token")

    # Check user_token is provided
    if not user_token:
        return Response({
            "message": "user_token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check user_token exists
    try:
        user = Register.objects.get(user_token=user_token)

    except Register.DoesNotExist:
        return Response({
            "message": "Invalid user_token"
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "message": "Logout successful",
    }, status=status.HTTP_200_OK)
