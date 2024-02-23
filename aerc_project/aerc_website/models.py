from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

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

class User(AbstractUser):
    GENDER_CHOICE = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('N', 'Prefer not to say')
    ]
    email = models.EmailField(
            max_length=255,
            unique=True,
        )
    first_name = models.CharField("first name", max_length=255, blank=True)
    last_name = models.CharField("last name", max_length=255, blank=True)
    gender = models.CharField(choices=GENDER_CHOICE, max_length=1, default='N')
    age = models.SmallIntegerField(default=18)
    profile = models.ImageField(upload_to=profile_path, default="")


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(choices=AssetType.CHOICES, max_length=1, default='O')
    current_value = models.DecimalField(default=0, max_digits=10, decimal_places=2)

class Vehicle(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    year = models.SmallIntegerField(default=2000)
    color = models.CharField(max_length=20, default='')
    brand =models.CharField(max_length=20, default='')
    VIN = models.CharField(max_length=30, unique=True, default='')
    model = models.CharField(max_length=20, default='')
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateField()

    class Meta:
        ordering = ["purchase_date"]
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    
class Stock(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    share = models.PositiveIntegerField(default=0)
    ticker_symbol = models.CharField(max_length=5, default='', db_index=True)
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        validators=[MinValueValidator(Decimal('0.00'))])
    market = models.CharField(max_length=10, default='', db_index=True)
    currency = models.CharField(max_length=3, default='')
    purchase_date = models.DateField()

    class Meta:
        ordering = ["ticker_symbol"]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ('ticker_symbol', 'market')
    
    def __str__(self):
        return f"{self.ticker_symbol} ({self.market})"

class StockTransaction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField()
    share = models.IntegerField(default=0)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        ordering = ["transaction_date"]
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"

    def __str__(self):
        return f"{self.stock.ticker_symbol} ({self.stock.market})"

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
    
class HousingIndex(models.Model):
    location = models.CharField(max_length=50, default='Canada')
    date = models.DateTimeField(default='1980-01-01')
    index = models.FloatField(default=0)