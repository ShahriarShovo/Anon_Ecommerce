#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from products.models import Category, SubCategory

def create_dummy_data():
    print("Creating dummy categories and subcategories...")
    
    # Create Categories
    categories_data = [
        {
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets',
            'is_active': True
        },
        {
            'name': 'Clothing',
            'description': 'Fashion and apparel',
            'is_active': True
        },
        {
            'name': 'Books',
            'description': 'Books and educational materials',
            'is_active': True
        },
        {
            'name': 'Home & Garden',
            'description': 'Home improvement and garden supplies',
            'is_active': True
        },
        {
            'name': 'Sports',
            'description': 'Sports equipment and accessories',
            'is_active': True
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        created_categories.append(category)
        if created:
            print(f"✓ Created category: {category.name}")
        else:
            print(f"→ Category already exists: {category.name}")
    
    # Create SubCategories
    subcategories_data = [
        # Electronics subcategories
        {
            'category': 'Electronics',
            'name': 'Smartphones',
            'description': 'Mobile phones and accessories',
            'is_active': True
        },
        {
            'category': 'Electronics',
            'name': 'Laptops',
            'description': 'Laptop computers and accessories',
            'is_active': True
        },
        {
            'category': 'Electronics',
            'name': 'Headphones',
            'description': 'Audio devices and headphones',
            'is_active': True
        },
        {
            'category': 'Electronics',
            'name': 'Cameras',
            'description': 'Digital cameras and photography equipment',
            'is_active': True
        },
        
        # Clothing subcategories
        {
            'category': 'Clothing',
            'name': 'Men\'s Fashion',
            'description': 'Men\'s clothing and accessories',
            'is_active': True
        },
        {
            'category': 'Clothing',
            'name': 'Women\'s Fashion',
            'description': 'Women\'s clothing and accessories',
            'is_active': True
        },
        {
            'category': 'Clothing',
            'name': 'Kids\' Clothing',
            'description': 'Children\'s clothing and accessories',
            'is_active': True
        },
        {
            'category': 'Clothing',
            'name': 'Shoes',
            'description': 'Footwear for all ages',
            'is_active': True
        },
        
        # Books subcategories
        {
            'category': 'Books',
            'name': 'Fiction',
            'description': 'Fiction books and novels',
            'is_active': True
        },
        {
            'category': 'Books',
            'name': 'Non-Fiction',
            'description': 'Educational and reference books',
            'is_active': True
        },
        {
            'category': 'Books',
            'name': 'Textbooks',
            'description': 'Academic and educational textbooks',
            'is_active': True
        },
        
        # Home & Garden subcategories
        {
            'category': 'Home & Garden',
            'name': 'Furniture',
            'description': 'Home and office furniture',
            'is_active': True
        },
        {
            'category': 'Home & Garden',
            'name': 'Kitchen & Dining',
            'description': 'Kitchen appliances and dining accessories',
            'is_active': True
        },
        {
            'category': 'Home & Garden',
            'name': 'Garden Tools',
            'description': 'Gardening equipment and tools',
            'is_active': True
        },
        
        # Sports subcategories
        {
            'category': 'Sports',
            'name': 'Fitness',
            'description': 'Fitness equipment and accessories',
            'is_active': True
        },
        {
            'category': 'Sports',
            'name': 'Outdoor Sports',
            'description': 'Outdoor sports equipment',
            'is_active': True
        },
        {
            'category': 'Sports',
            'name': 'Team Sports',
            'description': 'Team sports equipment and gear',
            'is_active': True
        }
    ]
    
    for subcat_data in subcategories_data:
        category_name = subcat_data.pop('category')
        category = Category.objects.get(name=category_name)
        
        subcategory, created = SubCategory.objects.get_or_create(
            category=category,
            name=subcat_data['name'],
            defaults=subcat_data
        )
        
        if created:
            print(f"✓ Created subcategory: {category.name} - {subcategory.name}")
        else:
            print(f"→ Subcategory already exists: {category.name} - {subcategory.name}")
    
    print("\n🎉 Dummy data creation completed!")
    print(f"Total Categories: {Category.objects.count()}")
    print(f"Total SubCategories: {SubCategory.objects.count()}")

if __name__ == '__main__':
    create_dummy_data()
