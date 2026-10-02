from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, CustomerProfile, AgentProfile, MechanicProfile,
    EWasteItem, RepairLog, Product, Order,
    Notification, ActivityLog, Gallery
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display  = ['username', 'email', 'role', 'is_staff', 'date_joined']
    list_filter   = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering      = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('E-Fix Hub', {'fields': ('role', 'phone', 'state', 'district', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('E-Fix Hub', {'fields': ('role', 'email')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone']
    search_fields = ['user__username']


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'qualification', 'verification_status', 'is_available']
    list_filter   = ['verification_status']
    search_fields = ['user__username']
    list_editable = ['verification_status']


@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'specialization', 'qualification', 'verification_status']
    list_filter   = ['verification_status']
    search_fields = ['user__username']
    list_editable = ['verification_status']


@admin.register(EWasteItem)
class EWasteItemAdmin(admin.ModelAdmin):
    list_display  = ['title', 'uploaded_by', 'category', 'status', 'created_at']
    list_filter   = ['status', 'category']
    search_fields = ['title', 'uploaded_by__username']


@admin.register(RepairLog)
class RepairLogAdmin(admin.ModelAdmin):
    list_display  = ['item', 'mechanic', 'cost', 'completed_at']
    search_fields = ['item__title', 'mechanic__username']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['linked_item', 'price', 'stock', 'is_published', 'is_sold']
    list_filter   = ['is_published', 'is_sold']
    list_editable = ['price', 'is_published']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'product', 'buyer', 'assigned_agent', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['buyer__username', 'product__linked_item__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'message', 'is_read', 'created_at']
    list_filter   = ['is_read']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ['user', 'action', 'timestamp']
    search_fields = ['user__username', 'action']


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display  = ['title', 'created_at']
