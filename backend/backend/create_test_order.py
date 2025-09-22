#!/usr/bin/env python
import os
import sys
import django
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import User
from orders.models.orders.order import Order
from orders.models.orders.address import Address
from orders.models.orders.order_item import OrderItem
from products.models import Product, ProductVariant

def create_test_order():
    try:
        # Get the test user
        user = User.objects.get(email='customer@test.com')
        print(f"Found user: {user.email}")
        
        # Get or create a test address
        address, created = Address.objects.get_or_create(
            user=user,
            full_name='Test Customer',
            phone_number='01234567890',
            city='Dhaka',
            address_line_1='123 Test Street',
            country='Bangladesh',
            defaults={
                'address_line_2': 'Test Area',
                'postal_code': '1000',
                'address_type': 'home'
            }
        )
        
        if created:
            print(f"Created new address: {address.id}")
        else:
            print(f"Using existing address: {address.id}")
        
        # Get a product (create one if none exists)
        product = Product.objects.first()
        if not product:
            print("No products found. Creating a test product...")
            product = Product.objects.create(
                title='Test Product',
                slug='test-product',
                price=100.00,
                old_price=120.00,
                description='Test product for delivered orders',
                category_id=1  # Assuming category 1 exists
            )
            print(f"Created test product: {product.id}")
        else:
            print(f"Using existing product: {product.title} (ID: {product.id})")
        
        # Create a test order
        order = Order.objects.create(
            user=user,
            delivery_address=address,
            subtotal=100.00,
            shipping_cost=0.00,
            tax_amount=0.00,
            total_amount=100.00,
            status='delivered',  # Set as delivered directly
            delivered_at=timezone.now(),
            notes='Test order for delivered status'
        )
        
        print(f"Created order: {order.order_number} (ID: {order.id})")
        
        # Create order item
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=100.00,
            total_price=100.00,
            product_name=product.title,
            product_sku=getattr(product, 'sku', 'TEST-SKU')
        )
        
        print(f"Created order item: {order_item.id}")
        
        print(f"\n✅ Test order created successfully!")
        print(f"Order Number: {order.order_number}")
        print(f"Status: {order.status}")
        print(f"Delivered At: {order.delivered_at}")
        print(f"Total Amount: ${order.total_amount}")
        
        return order
        
    except User.DoesNotExist:
        print("❌ User 'customer@test.com' not found. Please create the user first.")
        return None
    except Exception as e:
        print(f"❌ Error creating test order: {str(e)}")
        return None

if __name__ == '__main__':
    create_test_order()
