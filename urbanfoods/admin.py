from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'loyalty_points', 'is_verified', 'is_staff')
    list_filter = ('is_staff', 'is_verified', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'default_hostel', 'default_room', 'student_email', 'loyalty_points', 'is_verified')}),
    )

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'icon')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order', 'name')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'times_ordered')
    list_filter = ('category', 'is_available', 'is_featured', 'is_meal_of_day')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_featured')
    ordering = ('-is_featured', '-times_ordered', 'name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price', 'image')
        }),
        ('Availability & Features', {
            'fields': ('is_available', 'is_featured', 'is_meal_of_day', 'prep_time')
        }),
        ('Statistics', {
            'fields': ('times_ordered',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at', 'estimated_delivery')
    list_filter = ('status', 'created_at', 'estimated_delivery')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Delivery Details', {
            'fields': ('hostel', 'room_number', 'phone_number', 'delivery_notes', 'estimated_delivery')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'total', 'rating', 'review')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'quantity', 'price_at_order', 'subtotal')
    list_filter = ('order__status', 'food_item__category')
    search_fields = ('order__order_number', 'food_item__name')
    readonly_fields = ('subtotal',)

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp', 'notes')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('timestamp',)

@admin.register(FoodReview)
class FoodReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_item', 'order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'food_item__name', 'comment')
    readonly_fields = ('created_at',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'discount_percentage', 'discount_amount', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'code', 'description')
    list_editable = ('is_active',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'code')
        }),
        ('Discount Details', {
            'fields': ('discount_percentage', 'discount_amount', 'min_order_amount')
        }),
        ('Validity', {
            'fields': ('is_active', 'start_date', 'end_date', 'usage_limit', 'times_used')
        }),
    )
