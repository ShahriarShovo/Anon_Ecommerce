#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from products.models import Product, ProductReview
from accounts.models import User

def create_dummy_reviews():
    """Create dummy reviews for products"""
    
    # Get some products
    products = Product.objects.filter(status='active')[:5]
    
    if not products.exists():
        print("No active products found. Please create some products first.")
        return
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='reviewer@test.com',
        defaults={
            'is_active': True
        }
    )
    
    if created:
        print(f"Created test user: {user.email}")
    else:
        print(f"Using existing user: {user.email}")
    
    # Sample reviews data
    reviews_data = [
        {
            'rating': 5,
            'title': 'Excellent product!',
            'comment': 'Really love this product. Great quality and fast delivery.',
            'user_name': 'John Doe',
            'user_email': 'john@example.com'
        },
        {
            'rating': 4,
            'title': 'Good quality',
            'comment': 'Good product overall. Would recommend to others.',
            'user_name': 'Jane Smith',
            'user_email': 'jane@example.com'
        },
        {
            'rating': 5,
            'title': 'Amazing!',
            'comment': 'Exceeded my expectations. Will definitely buy again.',
            'user_name': 'Mike Johnson',
            'user_email': 'mike@example.com'
        },
        {
            'rating': 3,
            'title': 'Average product',
            'comment': 'It\'s okay, nothing special but does the job.',
            'user_name': 'Sarah Wilson',
            'user_email': 'sarah@example.com'
        },
        {
            'rating': 4,
            'title': 'Pretty good',
            'comment': 'Good value for money. Happy with the purchase.',
            'user_name': 'David Brown',
            'user_email': 'david@example.com'
        }
    ]
    
    created_count = 0
    
    for product in products:
        print(f"\nCreating reviews for: {product.title}")
        
        # Create 2-3 reviews per product
        for i, review_data in enumerate(reviews_data[:3]):
            # Check if review already exists
            existing_review = ProductReview.objects.filter(
                product=product,
                user_name=review_data['user_name']
            ).first()
            
            if existing_review:
                print(f"  Review already exists for {review_data['user_name']}")
                continue
            
            # Create new review
            review = ProductReview.objects.create(
                product=product,
                user=user if i == 0 else None,  # First review by authenticated user, others by guests
                rating=review_data['rating'],
                title=review_data['title'],
                comment=review_data['comment'],
                user_name=review_data['user_name'],
                user_email=review_data['user_email'],
                is_approved=True,  # Auto-approve for testing
                is_verified_purchase=True  # Mark as verified for testing
            )
            
            print(f"  Created review: {review_data['rating']} stars by {review_data['user_name']}")
            created_count += 1
    
    print(f"\n✅ Created {created_count} dummy reviews!")
    print("Reviews are now visible on the homepage product cards.")

if __name__ == '__main__':
    create_dummy_reviews()
