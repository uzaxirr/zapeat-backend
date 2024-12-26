from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CustomerProfile

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('mobile_number', 'is_active', 'date_joined', 'is_staff', 'is_customer', 'is_restaurant_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('mobile_number', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'password1', 'password2'),
        }),
    )
    
    inlines = [CustomerProfileInline]

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_orders')
    search_fields = ('user__mobile_number',)
    readonly_fields = ('created_at', 'updated_at')