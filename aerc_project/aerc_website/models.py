from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.utils import timezone as tz
from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    pre_init,
    post_init,
)
from .aes_enc import DataCipher
from .sha_hash import DataHasher

cipher = DataCipher(b"secret", b"123456")
hasher = DataHasher()

def Cipher():
    return cipher

def Hasher():
    return hasher

def profile_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"logo/{instance.name}.{ext}"
    return filename


class AssetType(models.Model):
    CHOICES = [
        ("C", "Crypto"),
        ("E", "Stock"),
        ("R", "Real Estate"),
        ("V", "Vehicle"),
        ("M", "Saving"),
        ("O", "Other"),
    ]


class PropertyType(models.Model):
    CHOICES = [
        ("SF", "Single-family"),
        ("MF", "Multi-family"),
        ("CD", "Condominium"),
        ("TH", "Townhouse"),
        ("AB", "Apartment Building"),
        ("CT", "Cottage"),
        ("CO", "Co-op (Cooperative housing)"),
        ("CP", "Commercial Property"),
        ("IP", "Industrial Property"),
        ("RS", "Retail Space"),
        ("OB", "Office Building"),
        ("WH", "Warehouse"),
        ("L", "Land"),
        ("F", "Farm"),
    ]

class LocationCategory(models.Model):
    CHOICES = [
        ("CA", "Canada"),
        ("AT", "Atlantic Region"),
        ("NL", "Newfoundland and Labrador"),
        ("SJ", "St. John's, Newfoundland and Labrador"),
        ("PEI", "Prince Edward Island"),
        ("CT", "Charlottetown, Prince Edward Island"),
        ("NS", "Nova Scotia"),
        ("HF", "Halifax, Nova Scotia"),
        ("NB", "New Brunswick"),
        ("SJFM", "Saint John, Fredericton, and Moncton, New Brunswick"),
        ("QC", "Quebec"),
        ("QEC", "Québec, Quebec"),
        ("SB", "Sherbrooke, Quebec"),
        ("TR", "Trois-Rivières, Quebec"),
        ("MTL", "Montréal, Quebec"),
        ("OGQ", "Ottawa-Gatineau, Quebec part, Ontario/Quebec"),
        ("ON", "Ontario"),
        ("OGO", "Ottawa-Gatineau, Ontario part, Ontario/Quebec"),
        ("OSW", "Oshawa, Ontario"),
        ("TNT", "Toronto, Ontario"),
        ("HT", "Hamilton, Ontario"),
        ("SC", "St. Catharines-Niagara, Ontario"),
        ("KCW", "Kitchener-Cambridge-Waterloo, Ontario"),
        ("GH", "Guelph, Ontario"),
        ("LD", "London, Ontario"),
        ("WS", "Windsor, Ontario"),
        ("SY", "Greater Sudbury, Ontario"),
        ("PR", "Prairie Region"),
        ("MT", "Manitoba"),
        ("WP", "Winnipeg, Manitoba"),
        ("SA", "Saskatchewan"),
        ("RGA", "Regina, Saskatchewan"),
        ("SKT", "Saskatoon, Saskatchewan"),
        ("ABT", "Alberta"),
        ("CGY", "Calgary, Alberta"),
        ("ED", "Edmonton, Alberta"),
        ("BC", "British Columbia"),
        ("KN", "Kelowna, British Columbia"),
        ("VNC", "Vancouver, British Columbia"),
        ("VCA", "Victoria, British Columbia"),
    ]


class User(AbstractUser):
    GENDER_CHOICE = [("F", "Female"), ("M", "Male"), ("N", "Prefer not to say")]
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    first_name = models.CharField("first name", max_length=255, blank=True)
    last_name = models.CharField("last name", max_length=255, blank=True)
    gender = models.CharField(choices=GENDER_CHOICE, max_length=1, default="N")
    age = models.SmallIntegerField(default=18)
    profile = models.ImageField(upload_to=profile_path, default="")
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False


@receiver(pre_save, sender=User)
def encrypt_user(sender, instance, **kwargs):
    instance.checksum = hasher.hash(
        instance.username,
        instance.email,
        instance.first_name,
        instance.last_name,
        instance.gender,
    )
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
            instance.checksumOk = hasher.verify(
                instance.checksum,
                instance.username,
                instance.email,
                instance.first_name,
                instance.last_name,
                instance.gender,
            )
        except:
            print("decrypt_user except")


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(choices=AssetType.CHOICES, max_length=1, default="O")
    purchase_price = models.FloatField(default=0)
    current_value = models.FloatField(default=0)

    class Meta:
        ordering = ['category']

    def __str__(self):
        for c in AssetType.CHOICES:
            if c[0] == str(self.category):
                return f"Asset ({c[1]})"
        return f"Asset ({self.category})"

class AssetHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    record_date = models.DateField()
    record_value = models.FloatField(default=0)

    class Meta:
        ordering = ["record_date", "id"]


class Vehicle(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    year = models.SmallIntegerField(default=2000)
    color = models.CharField(max_length=20, default="")
    brand = models.CharField(max_length=20, default="")
    VIN = models.CharField(max_length=30, default="")
    model = models.CharField(max_length=20, default="")
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
    instance.checksum = hasher.hash(
        instance.color, instance.brand, instance.VIN, instance.model
    )
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
            instance.checksumOk = hasher.verify(
                instance.checksum,
                instance.color,
                instance.brand,
                instance.VIN,
                instance.model,
            )
        except:
            print("decrypt_vehicle except")


class Stock(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    share = models.PositiveIntegerField(default=0)
    ticker_symbol = models.CharField(max_length=5, default="", db_index=True)
    purchase_price = models.FloatField()
    market = models.CharField(max_length=10, default="", db_index=True)
    currency = models.CharField(max_length=3, default="")
    purchase_date = models.DateField()
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

    class Meta:
        ordering = ["ticker_symbol"]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ("ticker_symbol", "market")

    def __str__(self):
        return f"{self.ticker_symbol} ({self.market})"

    def current_value(self):
        return self.share * self.purchase_price

    def update_on_transaction(self, transaction):
        if transaction.share > 0:
            total_purchase_price = (self.share * self.purchase_price) + (
                transaction.share * transaction.purchase_price
            )
            total_share = self.share + transaction.share
            self.purchase_price = total_purchase_price / total_share
            self.share = total_share
        else:
            self.share += transaction.share
        self.purchase_date = transaction.purchase_date
        self.save()


class StockTransaction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    share = models.IntegerField(default=0)
    purchase_date = models.DateField(null=True)
    purchase_price = models.FloatField(null=True)

    class Meta:
        ordering = ["purchase_date"]
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"

    def __str__(self):
        return f"{self.stock.ticker_symbol} ({self.stock.market})"


class Crypto(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    ticker_symbol = models.CharField(max_length=20, default="", db_index=True)
    name = models.CharField(max_length=256, default="")
    share = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="")
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateField()
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

    class Meta:
        ordering = ["ticker_symbol"]
        verbose_name = "Crypto"
        verbose_name_plural = "Cryptos"

    def __str__(self):
        return f"{self.ticker_symbol} {self.name}"
    
    def current_value(self):
        return self.share * self.purchase_price
    
    def update_on_transaction(self, transaction):
        if transaction.share > 0:
            total_purchase_price = (self.share * self.purchase_price) + (transaction.share * transaction.purchase_price)
            total_share = self.share + transaction.share
            self.purchase_price = total_purchase_price / total_share
            self.share = total_share
        else:
            self.share += transaction.share
        self.purchase_date = transaction.purchase_date
        self.save()


class CryptoTransaction(models.Model):
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    share = models.IntegerField(default=0)
    purchase_date = models.DateField(null=True)
    purchase_price = models.FloatField(default=0)

    class Meta:
        ordering = ["purchase_date"]
        verbose_name = "Crypto Transaction"
        verbose_name_plural = "Crypto Transactions"
    
    def __str__(self):
        return f"{self.crypto.ticker_symbol} {self.crypto.name}"


class House(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    address = models.CharField(default="", max_length=80)
    street_number = models.SmallIntegerField(blank=True, null=True)
    postal_code = models.CharField(default="XXX XXX", max_length=10)
    property_type = models.CharField(
        choices=PropertyType.CHOICES, max_length=5, default="SF"
    )
    location = models.CharField(
        choices=LocationCategory.CHOICES, max_length=5, default="CA"
    )
    lot_width = models.FloatField(default=0)
    lot_depth = models.FloatField(default=0)
    bedroom = models.SmallIntegerField(default=0)
    bathroom = models.SmallIntegerField(default=0)
    parking = models.SmallIntegerField(default=0)
    purchase_price = models.FloatField(default=0)
    purchase_date = models.DateTimeField(default=tz.now)
    checksum = models.CharField("checksum", max_length=255, blank=True)
    checksumOk = False

    @property
    def price_history(self):
        index_history = HousingIndex.objects.filter(
            location=self.get_location_display()
        ).order_by("-date")
        purchase_idx = index_history.filter(
            date__year=self.purchase_date.year, date__month=self.purchase_date.month
        ).first()
        purchase_idx_value = (
            purchase_idx.index if purchase_idx else index_history[0].index
        )  # Use index value from the purchasing month if exists
        recent = [r for r in index_history if self.purchase_date < r.date]
        history = recent if len(recent) > 120 else index_history[:120]
        return [
            {
                "month": r.date,
                "value": r.index / purchase_idx_value * self.purchase_price,
                "ratio": r.index / purchase_idx_value,
            }
            for r in history
        ]  # return record for last 10 years

    def __str__(self):
        return f"{self.street_number} {self.address}"

@receiver(pre_save, sender=House)
def encrypt_house(sender, instance, **kwargs):
    instance.checksum = hasher.hash(instance.property_type)
    instance.property_type = cipher.encrypt(instance.property_type)


@receiver(post_init, sender=House)
def decrypt_house(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        try:
            instance.property_type = cipher.decrypt(instance.property_type)
            instance.checksumOk = hasher.verify(
                instance.checksum, instance.property_type
            )
        except:
            print("decrypt_house except")


class HousingIndex(models.Model):
    location = models.CharField(max_length=50, default="Canada")
    date = models.DateTimeField(default="1980-01-01")
    index = models.FloatField(default=0)
