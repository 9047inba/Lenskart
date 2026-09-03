from django.db import models

import secrets

# Create your models here.


class Register(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,unique=True)
    email = models.EmailField(unique=True,null=True,blank=True)
    otp = models.CharField(max_length=4,null=True,blank=True)
    otp_created_at = models.DateTimeField(null=True,blank=True)
    user_token = models.CharField(max_length=64,unique=True,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Address(models.Model):

    ADDRESS_TYPE_CHOICES = (
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    )
    user = models.ForeignKey(Register,on_delete=models.CASCADE,related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=200,null=True,blank=True)
    address_type = models.CharField(max_length=20,choices=ADDRESS_TYPE_CHOICES,default="home")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"



class Order(models.Model):

    ORDER_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )
    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )
    user = models.ForeignKey(Register,on_delete=models.CASCADE,related_name="orders")
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS_CHOICES,default="pending")
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICES,default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"



class OrderItem(models.Model):

    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product_name = models.CharField(max_length=200)
    frame_color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    review = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.product_name


class Admin(models.Model):

    name = models.CharField(max_length=100,default="Jayakumar")
    phone = models.CharField(max_length=15,unique=True,default="7358906752")
    otp = models.CharField(max_length=4,null=True,blank=True)
    otp_created_at = models.DateTimeField(null=True,blank=True)
    user_token = models.CharField(max_length=64,unique=True,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.user_token:
            self.user_token = secrets.token_hex(32)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -------------------------------PRESCRIPTION---------------------------------------


class prescription(models.Model):

    name = models.CharField(max_length=100)
    birth_year = models.PositiveIntegerField()
    right_sph = models.DecimalField(max_digits=5,decimal_places=2)
    right_cyl = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    right_axis = models.IntegerField(null=True,blank=True)
    left_sph = models.DecimalField(max_digits=5,decimal_places=2)
    left_cyl = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    left_axis = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class glass_product(models.Model):

    CATEGORY_CHOICES = [
        ("eyeglasses", "Eyeglasses"),
        ("sunglasses", "Sunglasses"),
        ("power_glass", "Power Glass"),
        ("contact_lenses", "Contact Lenses"),
        ("computer_bluelight", "Computer & Blue Light"),
    ]
    FRAME_SIZE_CHOICES = [
        ("S", "Small (S)"),
        ("M", "Medium (M)"),
        ("L", "Large (L)"),
        ("XL", "Extra Large (XL)"),
    ]
    STRUCTURE_STYLE_CHOICES = [
        ("oval", "Oval"),
        ("square", "Square"),
        ("rectangle", "Rectangle"),
        ("round", "Round"),
        ("cat_eye", "Cat Eye"),
        ("aviator", "Aviator"),
        ("wayfarer", "Wayfarer"),
        ("geometric", "Geometric"),
        ("browline", "Browline"),
        ("clubmaster", "Clubmaster"),
        ("rimless", "Rimless"),
        ("semi_rimless", "Semi Rimless"),
        ("full_rim", "Full Rim"),
    ]
    TARGET_AUDIENCE_CHOICES = [
        ("unisex", "Unisex"),
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
    ]
    COLLECTION_TIER_CHOICES = [
        ("classic", "Classic"),
        ("executive", "Executive"),
        ("junior", "Junior"),
        ("essential", "Essential"),
        ("premium", "Premium"),
    ]
    model_name = models.CharField(max_length=200)
    category_type = models.CharField(max_length=50,choices=CATEGORY_CHOICES)
    frame_size = models.CharField(max_length=10,choices=FRAME_SIZE_CHOICES)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    color = models.CharField(max_length=100,null=True,blank=True)
    rating = models.DecimalField(max_digits=3,decimal_places=1,default=0.0)
    structure_style = models.CharField(max_length=50,choices=STRUCTURE_STYLE_CHOICES)
    target_audience = models.CharField(max_length=20,choices=TARGET_AUDIENCE_CHOICES)
    collection_tier = models.CharField(max_length=20,choices=COLLECTION_TIER_CHOICES)
    includes_adjustable_nose_pad = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model_name


# ------------------------------------------------------------------------------------------


class Wishlist(models.Model):

    user = models.ForeignKey(Register,on_delete=models.CASCADE,related_name="wishlist")
    product = models.ForeignKey(glass_product,on_delete=models.CASCADE,related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist"
            )
        ]

    def __str__(self):
        return f"{self.user.name} - {self.product.model_name}"


