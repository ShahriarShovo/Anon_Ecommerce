#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

def create_staff_user():
    print("Creating staff user...")
    
    # Create staff user
    staff_user, created = User.objects.get_or_create(
        email='staff@mail.com',
        defaults={
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        staff_user.set_password('staff123456')
        staff_user.save()
        print(f"✓ Created staff user: {staff_user.email}")
        print(f"  Password: staff123456")
        print(f"  Is Staff: {staff_user.is_staff}")
        print(f"  Is Active: {staff_user.is_active}")
    else:
        print(f"→ Staff user already exists: {staff_user.email}")
    
    # Create regular user (non-staff)
    regular_user, created = User.objects.get_or_create(
        email='user@mail.com',
        defaults={
            'is_staff': False,
            'is_active': True,
        }
    )
    
    if created:
        regular_user.set_password('user123456')
        regular_user.save()
        print(f"✓ Created regular user: {regular_user.email}")
        print(f"  Password: user123456")
        print(f"  Is Staff: {regular_user.is_staff}")
        print(f"  Is Active: {regular_user.is_active}")
    else:
        print(f"→ Regular user already exists: {regular_user.email}")
    
    print("\n🎉 User creation completed!")
    print(f"Total Users: {User.objects.count()}")
    print(f"Staff Users: {User.objects.filter(is_staff=True).count()}")
    print(f"Regular Users: {User.objects.filter(is_staff=False).count()}")

if __name__ == '__main__':
    create_staff_user()
