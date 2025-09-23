#!/usr/bin/env python
"""
Script to create dummy products with multiple images and variants
"""
import os
import sys
import django
from django.core.files import File
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from products.models import Product, ProductVariant, ProductImage, VariantOption
from products.models import Category, SubCategory

def create_dummy_image(color, size=(400, 400)):
    """Create a dummy image with specified color"""
    img = Image.new('RGB', size, color)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return File(img_io, name=f'dummy_{color}.jpg')

def create_dummy_products():
    """Create dummy products with variants and images"""
    
    # Get or create categories
    electronics, _ = Category.objects.get_or_create(
        name='Electronics',
        defaults={'slug': 'electronics', 'is_active': True}
    )
    
    phones, _ = SubCategory.objects.get_or_create(
        name='Smartphones',
        defaults={'category': electronics, 'slug': 'smartphones', 'is_active': True}
    )
    
    laptops, _ = SubCategory.objects.get_or_create(
        name='Laptops',
        defaults={'category': electronics, 'slug': 'laptops', 'is_active': True}
    )
    
    # Product 1: iPhone with variants
    print("Creating iPhone product...")
    iphone = Product.objects.create(
        title='iPhone 15 Pro',
        description='The latest iPhone with advanced features and premium design.',
        short_description='Premium smartphone with advanced camera system',
        category=electronics,
        subcategory=phones,
        product_type='variable',
        status='active',
        price=0,  # Variable product
        track_quantity=True,
        quantity=0,
        weight=0.187,
        weight_unit='kg',
        requires_shipping=True,
        taxable=True,
        featured=True,
        tags='smartphone, apple, premium, camera'
    )
    
    # Add images for iPhone
    colors = ['#1a1a1a', '#f5f5f5', '#8b4513', '#4169e1']  # Black, White, Brown, Blue
    for i, color in enumerate(colors):
        img = create_dummy_image(color)
        ProductImage.objects.create(
            product=iphone,
            image=img,
            alt_text=f'iPhone 15 Pro - {color}',
            caption=f'iPhone 15 Pro in {color} color',
            position=i + 1,
            is_primary=(i == 0)
        )
    
    # Create iPhone variants
    iphone_variants = [
        {
            'title': 'iPhone 15 Pro - Space Black - 128GB',
            'price': 999.00,
            'old_price': 1099.00,
            'quantity': 50,
            'option1_name': 'Color',
            'option1_value': 'Space Black',
            'option2_name': 'Storage',
            'option2_value': '128GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Space Black', 'position': 1},
                {'name': 'Storage', 'value': '128GB', 'position': 2}
            ]
        },
        {
            'title': 'iPhone 15 Pro - Space Black - 256GB',
            'price': 1099.00,
            'old_price': 1199.00,
            'quantity': 30,
            'option1_name': 'Color',
            'option1_value': 'Space Black',
            'option2_name': 'Storage',
            'option2_value': '256GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Space Black', 'position': 1},
                {'name': 'Storage', 'value': '256GB', 'position': 2}
            ]
        },
        {
            'title': 'iPhone 15 Pro - Natural Titanium - 128GB',
            'price': 999.00,
            'old_price': 1099.00,
            'quantity': 40,
            'option1_name': 'Color',
            'option1_value': 'Natural Titanium',
            'option2_name': 'Storage',
            'option2_value': '128GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Natural Titanium', 'position': 1},
                {'name': 'Storage', 'value': '128GB', 'position': 2}
            ]
        },
        {
            'title': 'iPhone 15 Pro - Natural Titanium - 256GB',
            'price': 1099.00,
            'old_price': 1199.00,
            'quantity': 25,
            'option1_name': 'Color',
            'option1_value': 'Natural Titanium',
            'option2_name': 'Storage',
            'option2_value': '256GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Natural Titanium', 'position': 1},
                {'name': 'Storage', 'value': '256GB', 'position': 2}
            ]
        }
    ]
    
    for i, variant_data in enumerate(iphone_variants):
        dynamic_options = variant_data.pop('dynamic_options', [])
        variant = ProductVariant.objects.create(
            product=iphone,
            position=i + 1,
            **variant_data
        )
        
        # Add dynamic options
        for option_data in dynamic_options:
            VariantOption.objects.create(
                variant=variant,
                name=option_data['name'],
                value=option_data['value'],
                position=option_data['position']
            )
    
    print(f"Created iPhone product with {len(iphone_variants)} variants")
    
    # Product 2: MacBook with variants
    print("Creating MacBook product...")
    macbook = Product.objects.create(
        title='MacBook Pro 14-inch',
        description='Powerful laptop with M3 chip for professional work.',
        short_description='Professional laptop with M3 chip',
        category=electronics,
        subcategory=laptops,
        product_type='variable',
        status='active',
        price=0,  # Variable product
        track_quantity=True,
        quantity=0,
        weight=1.6,
        weight_unit='kg',
        requires_shipping=True,
        taxable=True,
        featured=True,
        tags='laptop, apple, professional, m3'
    )
    
    # Add images for MacBook
    macbook_colors = ['#2c2c2c', '#f5f5f5', '#8b4513']  # Space Gray, Silver, Gold
    for i, color in enumerate(macbook_colors):
        img = create_dummy_image(color, (600, 400))
        ProductImage.objects.create(
            product=macbook,
            image=img,
            alt_text=f'MacBook Pro 14-inch - {color}',
            caption=f'MacBook Pro 14-inch in {color} color',
            position=i + 1,
            is_primary=(i == 0)
        )
    
    # Create MacBook variants
    macbook_variants = [
        {
            'title': 'MacBook Pro 14-inch - Space Gray - M3 - 512GB',
            'price': 1999.00,
            'old_price': 2199.00,
            'quantity': 20,
            'option1_name': 'Color',
            'option1_value': 'Space Gray',
            'option2_name': 'Chip',
            'option2_value': 'M3',
            'option3_name': 'Storage',
            'option3_value': '512GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Space Gray', 'position': 1},
                {'name': 'Chip', 'value': 'M3', 'position': 2},
                {'name': 'Storage', 'value': '512GB', 'position': 3}
            ]
        },
        {
            'title': 'MacBook Pro 14-inch - Space Gray - M3 - 1TB',
            'price': 2199.00,
            'old_price': 2399.00,
            'quantity': 15,
            'option1_name': 'Color',
            'option1_value': 'Space Gray',
            'option2_name': 'Chip',
            'option2_value': 'M3',
            'option3_name': 'Storage',
            'option3_value': '1TB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Space Gray', 'position': 1},
                {'name': 'Chip', 'value': 'M3', 'position': 2},
                {'name': 'Storage', 'value': '1TB', 'position': 3}
            ]
        },
        {
            'title': 'MacBook Pro 14-inch - Silver - M3 Pro - 512GB',
            'price': 2299.00,
            'old_price': 2499.00,
            'quantity': 12,
            'option1_name': 'Color',
            'option1_value': 'Silver',
            'option2_name': 'Chip',
            'option2_value': 'M3 Pro',
            'option3_name': 'Storage',
            'option3_value': '512GB',
            'dynamic_options': [
                {'name': 'Color', 'value': 'Silver', 'position': 1},
                {'name': 'Chip', 'value': 'M3 Pro', 'position': 2},
                {'name': 'Storage', 'value': '512GB', 'position': 3}
            ]
        }
    ]
    
    for i, variant_data in enumerate(macbook_variants):
        dynamic_options = variant_data.pop('dynamic_options', [])
        variant = ProductVariant.objects.create(
            product=macbook,
            position=i + 1,
            **variant_data
        )
        
        # Add dynamic options
        for option_data in dynamic_options:
            VariantOption.objects.create(
                variant=variant,
                name=option_data['name'],
                value=option_data['value'],
                position=option_data['position']
            )
    
    print(f"Created MacBook product with {len(macbook_variants)} variants")
    
    # Product 3: Simple Product
    print("Creating simple product...")
    airpods = Product.objects.create(
        title='AirPods Pro (2nd generation)',
        description='Premium wireless earbuds with active noise cancellation.',
        short_description='Wireless earbuds with noise cancellation',
        category=electronics,
        subcategory=phones,
        product_type='simple',
        status='active',
        price=249.00,
        old_price=279.00,
        track_quantity=True,
        quantity=100,
        weight=0.056,
        weight_unit='kg',
        requires_shipping=True,
        taxable=True,
        featured=False,
        tags='earbuds, wireless, noise cancellation'
    )
    
    # Add images for AirPods
    airpods_colors = ['#1a1a1a', '#f5f5f5']  # Black, White
    for i, color in enumerate(airpods_colors):
        img = create_dummy_image(color, (300, 300))
        ProductImage.objects.create(
            product=airpods,
            image=img,
            alt_text=f'AirPods Pro - {color}',
            caption=f'AirPods Pro in {color} color',
            position=i + 1,
            is_primary=(i == 0)
        )
    
    print("Created AirPods simple product")
    
    print("\n✅ Dummy products created successfully!")
    print(f"📱 iPhone 15 Pro: {len(iphone_variants)} variants, 4 images")
    print(f"💻 MacBook Pro 14-inch: {len(macbook_variants)} variants, 3 images")
    print(f"🎧 AirPods Pro: Simple product, 2 images")

if __name__ == '__main__':
    create_dummy_products()
