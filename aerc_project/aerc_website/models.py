from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, pre_init, post_init
from .aes_enc import DataCipher
from .sha_hash import DataHasher

cipher = DataCipher(b"secret", b"123456")
hasher = DataHasher()

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
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

@receiver(pre_save, sender=User)
def encrypt_user(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        instance.checksum = hasher.hash(instance.username, instance.email, instance.first_name, instance.last_name, instance.gender)
        instance.email = cipher.encrypt(instance.email)
        instance.first_name = cipher.encrypt(instance.first_name)
        instance.last_name = cipher.encrypt(instance.last_name)
        instance.gender = cipher.encrypt(instance.gender)

@receiver(post_init, sender=User)
def decrypt_user(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.email = cipher.decrypt(instance.email)
            instance.first_name = cipher.decrypt(instance.first_name)
            instance.last_name = cipher.decrypt(instance.last_name)
            instance.gender = cipher.decrypt(instance.gender)
            instance.checksumOk = hasher.verify(instance.checksum, instance.username, instance.email, instance.first_name, instance.last_name, instance.gender)
        except:
            print("decrypt_user except")

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
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

    class Meta:
        ordering = ["purchase_date"]
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

@receiver(pre_save, sender=Vehicle)
def encrypt_vehicle(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        instance.checksum = hasher.hash(instance.color, instance.brand, instance.VIN, instance.model)
        instance.color = cipher.encrypt(instance.color)
        instance.brand = cipher.encrypt(instance.brand)
        instance.VIN = cipher.encrypt(instance.VIN)
        instance.model = cipher.encrypt(instance.model)

@receiver(post_init, sender=Vehicle)
def decrypt_vehicle(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.color = cipher.decrypt(instance.color)
            instance.brand = cipher.decrypt(instance.brand)
            instance.VIN = cipher.decrypt(instance.VIN)
            instance.model = cipher.decrypt(instance.model)
            instance.checksumOk = hasher.verify(instance.checksum, instance.color, instance.brand, instance.VIN, instance.model)
        except:
            print("decrypt_vehicle except")
    
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
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

    class Meta:
        ordering = ["ticker_symbol"]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ('ticker_symbol', 'market')
    
    def __str__(self):
        return f"{self.ticker_symbol} ({self.market})"

@receiver(pre_save, sender=Stock)
def encrypt_stock(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        instance.checksum = hasher.hash(instance.ticker_symbol, instance.market, instance.currency)
        instance.ticker_symbol = cipher.encrypt(instance.ticker_symbol)
        instance.market = cipher.encrypt(instance.market)
        instance.currency = cipher.encrypt(instance.currency)

@receiver(post_init, sender=Stock)
def decrypt_stock(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.ticker_symbol = cipher.decrypt(instance.ticker_symbol)
            instance.market = cipher.decrypt(instance.market)
            instance.currency = cipher.decrypt(instance.currency)
            instance.checksumOk = hasher.verify(instance.checksum, instance.ticker_symbol, instance.market, instance.currency)
        except:
            print("decrypt_stock except")

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
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

@receiver(pre_save, sender=Crypto)
def encrypt_crypto(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        instance.checksum = hasher.hash(instance.coin_name)
        instance.coin_name = cipher.encrypt(instance.coin_name)

@receiver(post_init, sender=Crypto)
def decrypt_crypto(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.coin_name = cipher.decrypt(instance.coin_name)
            instance.checksumOk = hasher.verify(instance.checksum, instance.coin_name)
        except:
            print("decrypt_crypto except")

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
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

@receiver(pre_save, sender=House)
def encrypt_house(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        instance.checksum = hasher.hash(instance.property_type)
        instance.property_type = cipher.encrypt(instance.property_type)

@receiver(post_init, sender=House)
def decrypt_house(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.property_type = cipher.decrypt(instance.property_type)
            instance.checksumOk = hasher.verify(instance.checksum, instance.property_type)
        except:
            print("decrypt_house except")
    
class HousingIndex(models.Model):
    location = models.CharField(max_length=50, default='Canada')
    date = models.DateTimeField(default='1980-01-01')
    index = models.FloatField(default=0)