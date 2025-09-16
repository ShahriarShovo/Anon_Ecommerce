#!/usr/bin/env python3
"""
Direct database test for product creation
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from products.models import Product, ProductVariant, ProductImage, Category, SubCategory, VariantOption

def create_test_data():
    """Create test products directly in database"""
    print("🚀 Creating test data directly in database...")
    
    try:
        # Get or create category and subcategory
        category, created = Category.objects.get_or_create(
            name="Test Category",
            defaults={
                'description': 'Test category for product testing',
                'is_active': True
            }
        )
        print(f"Category: {'Created' if created else 'Found'} - {category.name}")
        
        subcategory, created = SubCategory.objects.get_or_create(
            name="Test SubCategory",
            defaults={
                'category': category,
                'description': 'Test subcategory for product testing',
                'is_active': True
            }
        )
        print(f"SubCategory: {'Created' if created else 'Found'} - {subcategory.name}")
        
        # Create simple product
        simple_product = Product.objects.create(
            title="Test Simple Product",
            description="This is a test simple product created directly",
            short_description="Test simple product",
            category=category,
            subcategory=subcategory,
            product_type="simple",
            status="active",
            price=25.99,
            old_price=35.99,
            track_quantity=True,
            quantity=100,
            allow_backorder=False,
            weight_unit="kg",
            requires_shipping=True,
            taxable=True,
            featured=False
        )
        print(f"✅ Simple Product created: {simple_product.title} (ID: {simple_product.id})")
        
        # Create variable product
        variable_product = Product.objects.create(
            title="Test Variable Product",
            description="This is a test variable product with variants",
            short_description="Test variable product",
            category=category,
            subcategory=subcategory,
            product_type="variable",
            status="active",
            price=15.00,
            old_price=25.00,
            track_quantity=True,
            quantity=50,
            allow_backorder=False,
            weight_unit="kg",
            requires_shipping=True,
            taxable=True,
            featured=False,
            option1_name="Size",
            option2_name="Color"
        )
        print(f"✅ Variable Product created: {variable_product.title} (ID: {variable_product.id})")
        
        # Create variants for variable product
        variant1 = ProductVariant.objects.create(
            product=variable_product,
            title="Small Red",
            sku="TEST-SMALL-RED",
            price=10.00,
            old_price=15.00,
            quantity=20,
            track_quantity=True,
            allow_backorder=False,
            weight_unit="kg",
            position=1,
            is_active=True,
            option1_name="Size",
            option1_value="Small",
            option2_name="Color",
            option2_value="Red"
        )
        print(f"✅ Variant 1 created: {variant1.title} (ID: {variant1.id})")
        
        # Add dynamic options to variant1
        VariantOption.objects.create(
            variant=variant1,
            name="Size",
            value="Small",
            position=1
        )
        VariantOption.objects.create(
            variant=variant1,
            name="Color",
            value="Red",
            position=2
        )
        print(f"✅ Dynamic options added to variant 1")
        
        variant2 = ProductVariant.objects.create(
            product=variable_product,
            title="Large Blue",
            sku="TEST-LARGE-BLUE",
            price=20.00,
            old_price=30.00,
            quantity=15,
            track_quantity=True,
            allow_backorder=False,
            weight_unit="kg",
            position=2,
            is_active=True,
            option1_name="Size",
            option1_value="Large",
            option2_name="Color",
            option2_value="Blue"
        )
        print(f"✅ Variant 2 created: {variant2.title} (ID: {variant2.id})")
        
        # Add dynamic options to variant2
        VariantOption.objects.create(
            variant=variant2,
            name="Size",
            value="Large",
            position=1
        )
        VariantOption.objects.create(
            variant=variant2,
            name="Color",
            value="Blue",
            position=2
        )
        print(f"✅ Dynamic options added to variant 2")
        
        # Test variant methods
        print(f"\n📊 Testing Variant Methods:")
        print(f"Variant 1 all_options: {variant1.get_all_options()}")
        print(f"Variant 1 dynamic_options: {variant1.get_dynamic_options()}")
        print(f"Variant 1 display_price: {variant1.display_price}")
        print(f"Variant 1 discount_percentage: {variant1.discount_percentage}")
        
        # Test product methods
        print(f"\n📊 Testing Product Methods:")
        print(f"Variable product primary_image: {variable_product.primary_image}")
        print(f"Variable product variant_count: {variable_product.variants.count()}")
        
        print(f"\n✅ All test data created successfully!")
        print(f"📋 Summary:")
        print(f"  - Simple Product: {simple_product.title} (ID: {simple_product.id})")
        print(f"  - Variable Product: {variable_product.title} (ID: {variable_product.id})")
        print(f"  - Variants: {variable_product.variants.count()}")
        print(f"  - Dynamic Options: {VariantOption.objects.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print(f"\n🌐 Testing API Endpoints:")
    
    try:
        import requests
        
        # Test product list endpoint
        response = requests.get("http://127.0.0.1:8000/api/products/product/")
        print(f"Product List API: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            print(f"  - Found {len(products)} products via API")
            for product in products:
                print(f"    * {product.get('title')} (Type: {product.get('product_type')})")
        
        # Test product detail endpoint
        if products:
            product_id = products[0]['id']
            response = requests.get(f"http://127.0.0.1:8000/api/products/product/{product_id}/")
            print(f"Product Detail API: {response.status_code}")
            
            if response.status_code == 200:
                product_detail = response.json()
                print(f"  - Product: {product_detail.get('title')}")
                print(f"  - Variants: {len(product_detail.get('variants', []))}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    success = create_test_data()
    if success:
        test_api_endpoints()
    
    print(f"\n🎯 Test completed!")
