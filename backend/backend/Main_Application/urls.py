
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
            'accounts': '/accounts/',
            'admin': '/admin/',
            'api_docs': '/docs/'
        },
        'product_endpoints': {
            'list': '/api/products/product/',
            'detail': '/api/products/product/{slug}/',
            'categories': '/api/products/category/',
            'subcategories': '/api/products/subcategory/'
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
    path('accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
