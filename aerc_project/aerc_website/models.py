from django.db import models
from django.contrib.auth.models import AbstractBaseUser

def profile_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'logo/{instance.name}.{ext}'
    return filename

class AssetType(models.Model):
    CHOICES = [
        ('C', 'Crypto'),
        ('E', 'Stock'),
        ('R', 'Real Estate'),
        ('V', 'Vehicle'),
        ('M', 'Saving'),
        ('O', 'Other')
    ]

class User(AbstractBaseUser):
    GENDER_CHOICE = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('N', 'Prefer not to say')
    ]
    email = models.EmailField(
            max_length=255,
            unique=True,
        )
    gender = models.CharField(choices=GENDER_CHOICE, max_length=1, default='N')
    age =  models.SmallIntegerField(default=18)
    profile = models.ImageField(upload_to=profile_path, default="")
    USERNAME_FIELD = "email"


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(choices=AssetType.CHOICES, max_length=1, default='O')
    current_value = models.FloatField(default=0)

class Vehicle(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    year = models.SmallIntegerField(default=2000)
    color = models.CharField(max_length=20, default='Black')
    brand =models.CharField(max_length=20, default='Ford')
    VIN = models.CharField(max_length=30, default='')
    model = models.CharField(max_length=20, default='')
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateTimeField(auto_now_add=True)
    
class Stock(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    share = models.SmallIntegerField(default=0)
    symbol = models.CharField(max_length=10, default='')
    dividend = models.FloatField(default=0)
    purchase_price = models.FloatField(default=0)
    market = models.CharField(max_length=10, default='')
    currency = models.CharField(max_length=10, default='')
    purchase_date = models.DateTimeField(auto_now_add=True)

class Crypto(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=10, default='')
    amount = models.IntegerField(default=0)
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateTimeField(auto_now_add=True)

class House(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    property_type = models.CharField(max_length=10, default='')
    lot_width = models.FloatField(default=0)
    lot_depth = models.FloatField(default=0)
    bedroom = models.SmallIntegerField(default=0)
    bathroom = models.SmallIntegerField(default=0)
    parking = models.SmallIntegerField(default=0)
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateTimeField(auto_now_add=True)