from django.contrib import admin
from invoice.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'status', 'invoice_date', 'due_date']
    list_filter = ['status', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'order__order_number', 'order__user__email']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('order', 'invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_logo', 'company_address', 'company_phone', 'company_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
