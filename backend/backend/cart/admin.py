from django.contrib import admin
from cart.models import Cart, CartItem, Wishlist, WishlistItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model"""
    list_display = [
        'id', 'user', 'session_key', 'total_items', 
        'subtotal', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'subtotal']
    ordering = ['-updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem model"""
    list_display = [
        'id', 'cart', 'product', 'variant', 'quantity', 
        'unit_price', 'get_total_price', 'added_at'
    ]
    list_filter = ['added_at', 'product__category']
    search_fields = ['product__title', 'cart__user__email']
    readonly_fields = ['added_at', 'updated_at']
    ordering = ['-added_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cart', 'product', 'variant'
        )
    
    def get_total_price(self, obj):
        """Display total price for this cart item"""
        return f"৳{obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin interface for Wishlist model"""
    list_display = [
        'id', 'user', 'name', 'get_total_items', 
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def get_total_items(self, obj):
        """Display total items in wishlist"""
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin interface for WishlistItem model"""
    list_display = [
        'id', 'wishlist', 'product', 'variant', 
        'get_current_price', 'is_available', 'added_at'
    ]
    list_filter = ['added_at', 'product__category']
    search_fields = ['product__title', 'wishlist__user__email']
    readonly_fields = ['added_at']
    ordering = ['-added_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'wishlist', 'product', 'variant'
        )
    
    def get_current_price(self, obj):
        """Display current price of the item"""
        return f"৳{obj.get_current_price():.2f}"
    get_current_price.short_description = 'Current Price'
    
    def is_available(self, obj):
        """Display availability status"""
        return obj.is_available()
    is_available.boolean = True
    is_available.short_description = 'Available'
