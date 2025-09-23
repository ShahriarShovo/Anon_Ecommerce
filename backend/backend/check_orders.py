#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from orders.models.orders.order import Order

print("=== Orders in Database ===")
total_orders = Order.objects.count()
print(f"Total orders: {total_orders}")

if total_orders > 0:
    for order in Order.objects.all():
        print(f"Order {order.id}: {order.order_number} - {order.user.email} - {order.status}")
        print(f"  Created: {order.created_at}")
        print(f"  Total: ${order.total_amount}")
        print()
else:
    print("No orders found in database")
