from django.db import models

# Create your models here.


class Register(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    user_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

# Login
class Login(models.Model):

    user = models.ForeignKey(Register,on_delete=models.CASCADE,related_name="logins")
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone 
    
