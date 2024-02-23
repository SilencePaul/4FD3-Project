from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    list_filter = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    search_fields = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    ordering = ('brand', 'model', 'year', 'color', 'VIN', 'purchase_price', 'purchase_date')
    list_per_page = 25
