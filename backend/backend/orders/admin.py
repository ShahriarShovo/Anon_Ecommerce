from django.contrib import admin
from orders.models.orders.address import Address
from orders.models.orders.order import Order
from orders.models.orders.order_item import OrderItem
from orders.models.payments.payment import Payment
from orders.models.payments.payment_method import PaymentMethod

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'city', 'country', 'is_default', 'user', 'created_at']
    list_filter = ['city', 'country', 'is_default', 'address_type', 'created_at']
    search_fields = ['full_name', 'phone_number', 'city', 'address_line_1']
    readonly_fields = ['created_at', 'updated_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'variant_title', 'unit_price', 'total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'delivery_address__city']
    search_fields = ['order_number', 'user__email', 'delivery_address__full_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'variant_title', 'quantity', 'unit_price', 'total_price']
    list_filter = ['created_at']
    search_fields = ['product_name', 'product_sku', 'order__order_number']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type', 'is_active', 'is_cod', 'display_order']
    list_filter = ['method_type', 'is_active', 'is_cod']
    search_fields = ['name', 'description']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'status', 'cod_collected', 'created_at']
    list_filter = ['status', 'payment_method__method_type', 'cod_collected', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'cod_collected_at']
