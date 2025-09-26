
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

def api_info(request):
    return JsonResponse({
        'message': 'Anon eCommerce API',
        'version': 'v1',
        'status': 'active',
        'endpoints': {
            'products': '/api/products/',
            'cart': '/api/cart/',
            'wishlist': '/api/wishlist/',
            'accounts': '/accounts/',
            'admin': '/admin/',
            'api_docs': '/docs/'
        },
        'product_endpoints': {
            'list': '/api/products/product/',
            'detail': '/api/products/product/{slug}/',
            'categories': '/api/products/category/',
            'subcategories': '/api/products/subcategory/'
        },
        'cart_endpoints': {
            'add_item': '/api/cart/add/',
            'get_cart': '/api/cart/',
            'increase_quantity': '/api/cart/items/{id}/increase/',
            'decrease_quantity': '/api/cart/items/{id}/decrease/',
            'clear_cart': '/api/cart/clear/'
        },
        'wishlist_endpoints': {
            'add_item': '/api/wishlist/add/',
            'get_wishlist': '/api/wishlist/',
            'remove_item': '/api/wishlist/items/{id}/remove/'
        },
        'order_endpoints': {
            'create_order': '/api/orders/create/',
            'list_orders': '/api/orders/',
            'order_detail': '/api/orders/{id}/',
            'payment_methods': '/api/orders/payment-methods/'
        },
        'invoice_endpoints': {
            'generate_invoice': '/api/invoice/generate/{order_id}/',
            'list_invoices': '/api/invoice/',
            'invoice_detail': '/api/invoice/{id}/',
            'invoice_pdf': '/api/invoice/{id}/pdf/',
            'download_invoice': '/api/invoice/{id}/download/'
        }
    })

def api_docs(request):
    return render(request, 'api_docs.html')

urlpatterns = [
    # API info at root URL
    path('', api_info, name='api-info'),
    
    # API documentation
    path('docs/', api_docs, name='api-docs'),
    
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/', include('cart.urls')),  # Cart and Wishlist APIs
    path('api/orders/', include('orders.urls')),  # Orders APIs
    path('api/analytics/', include('analytics.urls')),  # Analytics APIs
    path('api/invoice/', include('invoice.urls')),  # Invoice APIs
    path('api/settings/', include('settings.urls')),  # Settings APIs
    path('', include('chat_and_notifications.urls')),  # Chat APIs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
