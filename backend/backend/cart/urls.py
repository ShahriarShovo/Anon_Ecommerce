"""
Cart URLs
=========

This module defines URL patterns for cart and wishlist functionality.
All URLs are prefixed with 'api/cart/' and 'api/wishlist/'.

URL Patterns:
- Cart Operations:
  - POST /api/cart/add/ - Add item to cart
  - POST /api/cart/items/{id}/increase/ - Increase item quantity
  - POST /api/cart/items/{id}/decrease/ - Decrease item quantity
  - GET /api/cart/ - Get user's cart
  - DELETE /api/cart/clear/ - Clear cart

- Wishlist Operations:
  - POST /api/wishlist/add/ - Add item to wishlist
  - DELETE /api/wishlist/items/{id}/remove/ - Remove item from wishlist
  - GET /api/wishlist/ - Get user's wishlist
"""

from django.urls import path, include
from .views.cart import (
    add_to_cart,
    increase_cart_item_quantity,
    decrease_cart_item_quantity,
    remove_cart_item,
    get_cart
)
from .views.clear_cart import clear_cart
from .views.wishlist import (
    add_to_wishlist,
    remove_from_wishlist,
    get_wishlist
)

# Cart URL patterns
cart_urlpatterns = [
    # Cart operations
    path('add/', add_to_cart, name='add-to-cart'),
    path('items/<int:item_id>/increase/', increase_cart_item_quantity, name='increase-cart-item'),
    path('items/<int:item_id>/decrease/', decrease_cart_item_quantity, name='decrease-cart-item'),
    path('items/<int:item_id>/remove/', remove_cart_item, name='remove-cart-item'),
    path('', get_cart, name='get-cart'),
    path('clear/', clear_cart, name='clear-cart'),
]

# Wishlist URL patterns
wishlist_urlpatterns = [
    # Wishlist operations
    path('add/', add_to_wishlist, name='add-to-wishlist'),
    path('items/<int:item_id>/remove/', remove_from_wishlist, name='remove-from-wishlist'),
    path('', get_wishlist, name='get-wishlist'),
]

# Combined URL patterns
urlpatterns = [
    # Cart URLs with 'cart/' prefix
    path('cart/', include(cart_urlpatterns)),
    
    # Wishlist URLs with 'wishlist/' prefix
    path('wishlist/', include(wishlist_urlpatterns)),
]
