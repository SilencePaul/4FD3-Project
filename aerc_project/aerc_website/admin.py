from django.contrib import admin
from .models import *

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    list_filter = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    search_fields = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    ordering = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    list_per_page = 25

admin.site.register(User)
admin.site.register(Asset)
admin.site.register(Stock)
admin.site.register(Crypto)
admin.site.register(House)
admin.site.register(HousingIndex)