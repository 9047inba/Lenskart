from django.urls import path
from .views import *

urlpatterns = [

    # Authentication
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("verify-otp/", verify_otp , name="verify-otp"),
    path("logout/", logout_user, name="logout"),

    # Profile
    path("profile/", profile, name="profile"),

    # Address
    path("address/save/", save_address, name="address_save"),
    path("address/delete/<int:address_id>/", delete_address, name="address_delete"),

    # Orders
    path("orders/", order_history, name="orders"),

    #Prescription
    path("prescription/",prescription_get_api,name="prescription"),
    path("prescription/create/",prescription_post_api,name="prescription_create"),
    path("glass-product/",glass_product_get_api,name="glass_product_get"),

    # GLASS PRODUCT
    path("glass-product/create/",glass_product_post_api,name="glass_product_post"),

    #Wishlist
    path("wishlist/",add_wishlist,name="add_wishlist"),

    path("eyeglasses/",eyeglasses,name="eyeglasses"),
    path("sunglasses/",sunglasses,name="sunglasses"),

    path("search/",search_products,name="search_products"),
]

