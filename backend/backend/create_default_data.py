#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.permission_models import Permission, Role, RolePermission

def create_default_permissions():
    """Create default system permissions"""
    default_permissions = [
        {'name': 'Dashboard Access', 'codename': 'dashboard_access', 'category': 'dashboard'},
        {'name': 'Manage Products', 'codename': 'manage_products', 'category': 'products'},
        {'name': 'Manage Orders', 'codename': 'manage_orders', 'category': 'orders'},
        {'name': 'Manage Archived Products', 'codename': 'manage_archived_products', 'category': 'products'},
        {'name': 'Manage Categories', 'codename': 'manage_categories', 'category': 'products'},
        {'name': 'Manage Subcategories', 'codename': 'manage_subcategories', 'category': 'products'},
        {'name': 'Manage Users', 'codename': 'manage_users', 'category': 'users'},
        {'name': 'Manage Admin Staff', 'codename': 'manage_admin_staff', 'category': 'users'},
        {'name': 'Inbox Access', 'codename': 'inbox_access', 'category': 'communication'},
        {'name': 'Live Chat Access', 'codename': 'live_chat_access', 'category': 'communication'},
        {'name': 'Contact Messages', 'codename': 'contact_messages', 'category': 'communication'},
        {'name': 'Order Tracking', 'codename': 'order_tracking', 'category': 'orders'},
        {'name': 'Reports Access', 'codename': 'reports_access', 'category': 'reports'},
        {'name': 'Settings Access', 'codename': 'settings_access', 'category': 'settings'},
    ]

    created_permissions = []
    for perm_data in default_permissions:
        permission, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            defaults=perm_data
        )
        if created:
            created_permissions.append(permission.name)
        print(f"Permission: {permission.name} - {'Created' if created else 'Already exists'}")

    return created_permissions

def create_default_roles():
    """Create default roles with permissions"""
    default_roles = [
        {
            'name': 'Super Admin',
            'description': 'Full system access with all permissions',
            'is_system_role': True,
            'permissions': [
                'dashboard_access', 'manage_products', 'manage_orders', 
                'manage_archived_products', 'manage_categories', 'manage_subcategories',
                'manage_users', 'manage_admin_staff', 'inbox_access', 
                'live_chat_access', 'contact_messages', 'order_tracking',
                'reports_access', 'settings_access'
            ]
        },
        {
            'name': 'Product Manager',
            'description': 'Can manage products, categories, and orders',
            'is_system_role': True,
            'permissions': [
                'dashboard_access', 'manage_products', 'manage_orders', 
                'manage_categories', 'manage_subcategories', 'order_tracking'
            ]
        },
        {
            'name': 'Customer Support',
            'description': 'Can handle customer inquiries and order tracking',
            'is_system_role': True,
            'permissions': [
                'dashboard_access', 'manage_orders', 'inbox_access', 
                'live_chat_access', 'contact_messages', 'order_tracking'
            ]
        },
        {
            'name': 'Content Manager',
            'description': 'Can manage products and categories',
            'is_system_role': True,
            'permissions': [
                'dashboard_access', 'manage_products', 'manage_categories', 
                'manage_subcategories', 'manage_archived_products'
            ]
        }
    ]

    created_roles = []
    for role_data in default_roles:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description'],
                'is_system_role': role_data['is_system_role']
            }
        )
        if created:
            created_roles.append(role.name)
            print(f"Role: {role.name} - Created")
        else:
            print(f"Role: {role.name} - Already exists")
        
        # Assign permissions to role
        for perm_codename in role_data['permissions']:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                role_permission, created = RolePermission.objects.get_or_create(
                    role=role, 
                    permission=permission
                )
                if created:
                    print(f"  - Assigned permission: {permission.name}")
            except Permission.DoesNotExist:
                print(f"  - Permission not found: {perm_codename}")

    return created_roles

if __name__ == '__main__':
    print("Creating default permissions and roles...")
    print("=" * 50)
    
    # Create permissions
    print("\n1. Creating Permissions:")
    created_permissions = create_default_permissions()
    
    # Create roles
    print("\n2. Creating Roles:")
    created_roles = create_default_roles()
    
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"- Created {len(created_permissions)} new permissions")
    print(f"- Created {len(created_roles)} new roles")
    print("=" * 50)
