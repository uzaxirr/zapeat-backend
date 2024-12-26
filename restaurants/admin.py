from django.contrib import admin
from .models import (
    OpeningTime,
    BankAccount,
    Location,
    Restaurant,
    MenuCategory,
    MenuItem,
    CustomizationGroup,
    CustomizationOption,
)

@admin.register(OpeningTime)
class OpeningTimeAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'from_hour', 'to_hour')
    ordering = ['weekday']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'account_number', 'bank_name', 'ifsc_code')
    search_fields = ('account_name', 'account_number', 'ifsc_code')
    list_filter = ('bank_name',)
    ordering = ['created_at']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude')
    search_fields = ('latitude', 'longitude')

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'mobile_number', 'email', 'is_online')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('category', 'is_online')
    ordering = ['-created_at']
    filter_horizontal = ('opening_times', 'bank_accounts')  # For many-to-many fields

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    search_fields = ('name',)
    list_filter = ('restaurant',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'food_type', 'customizable', 'spice_level', 'sweetness_level', 'must_try')
    search_fields = ('name',)
    list_filter = ('food_type', 'customizable')
    ordering = ['name']

@admin.register(CustomizationGroup)
class CustomizationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_item', 'max_options_allowed', 'min_options_allowed')
    search_fields = ('name',)
    list_filter = ('menu_item',)

@admin.register(CustomizationOption)
class CustomizationOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'price', 'food_type', 'spice_level', 'sweetness_level')
    search_fields = ('name',)
    list_filter = ('food_type', 'group')
