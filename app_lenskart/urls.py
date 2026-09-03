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

    # SELECT LENS
    path("select-lenses/<int:product_id>/",select_lens_api,name="select_lens_api"),

    # GLASS PRODUCT
    path("glass-product/create/",glass_product_post_api,name="glass_product_post"),
    path("glass-product/",glass_product_get_api,name="glass_product_get"),

    #Wishlist
    path("wishlist/",add_wishlist,name="add_wishlist"),

    #filters
    path("eyeglasses/",eyeglasses,name="eyeglasses"),
    path("sunglasses/",sunglasses,name="sunglasses"),
    path("buy-one-get-one/", buy_one_get_one_products, name="buy-one-get-one" ),

    path("search/",search_products,name="search_products"),

    path("checkout/",checkout_api,name="checkout"),

    path("product-details/", product_details, name="product-details" ),

    path("product/", product_api, name="product_api"),
    path("product/delete/<int:id>/",glass_product_delete_api,name="glass_product_delete_api"),
    path("kids-club/",kids_club_api,name="kids_club"),

]