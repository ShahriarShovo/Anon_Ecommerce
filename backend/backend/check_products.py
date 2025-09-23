#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from products.models import Product, ProductVariant, VariantOption

# Check iPhone variants
print("=== iPhone 15 Pro Variants ===")
iphone = Product.objects.get(title='iPhone 15 Pro')
for variant in iphone.variants.all():
    print(f"Variant: {variant.title}")
    print(f"  Legacy: {variant.option1_name}={variant.option1_value}, {variant.option2_name}={variant.option2_value}")
    dynamic_options = variant.dynamic_options.all()
    if dynamic_options:
        print(f"  Dynamic: {[f'{opt.name}={opt.value}' for opt in dynamic_options]}")
    print()

# Check MacBook variants
print("=== MacBook Pro 14-inch Variants ===")
macbook = Product.objects.get(title='MacBook Pro 14-inch')
for variant in macbook.variants.all():
    print(f"Variant: {variant.title}")
    print(f"  Legacy: {variant.option1_name}={variant.option1_value}, {variant.option2_name}={variant.option2_value}, {variant.option3_name}={variant.option3_value}")
    dynamic_options = variant.dynamic_options.all()
    if dynamic_options:
        print(f"  Dynamic: {[f'{opt.name}={opt.value}' for opt in dynamic_options]}")
    print()

# Check images
print("=== Product Images ===")
for product in [iphone, macbook]:
    print(f"{product.title}: {product.images.count()} images")
    for img in product.images.all():
        print(f"  - {img.alt_text} (Primary: {img.is_primary})")
    print()
