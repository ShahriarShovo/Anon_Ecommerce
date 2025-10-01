#!/usr/bin/env python
"""
Script to fix multiple primary email settings issue
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from settings.email_model import EmailSettings

def fix_primary_emails():
    """Fix multiple primary email settings by keeping only one primary"""
    print("🔍 Checking current primary email settings...")
    
    # Get all primary email settings
    primary_emails = EmailSettings.objects.filter(is_primary=True)
    print(f"Found {primary_emails.count()} primary email settings:")
    
    for email in primary_emails:
        print(f"  - ID: {email.id}, Name: {email.name}, Email: {email.email_address}, Created by: {email.created_by.username}")
    
    if primary_emails.count() > 1:
        print("\n⚠️  Multiple primary emails found! Fixing...")
        
        # Keep the first one as primary, unset others
        first_primary = primary_emails.first()
        others = primary_emails.exclude(id=first_primary.id)
        
        print(f"✅ Keeping ID {first_primary.id} as primary")
        print(f"❌ Unsetting primary for {others.count()} others")
        
        # Unset primary for others
        others.update(is_primary=False)
        
        print("\n✅ Fixed! Now only one primary email exists.")
        
        # Verify the fix
        remaining_primary = EmailSettings.objects.filter(is_primary=True)
        print(f"✅ Verification: {remaining_primary.count()} primary email(s) remaining")
        
    elif primary_emails.count() == 1:
        print("✅ Only one primary email found - no fix needed!")
        
    else:
        print("⚠️  No primary emails found!")
        
        # Make the first active email as primary
        first_active = EmailSettings.objects.filter(is_active=True).first()
        if first_active:
            first_active.is_primary = True
            first_active.save()
            print(f"✅ Set ID {first_active.id} as primary")
        else:
            print("❌ No active emails found to set as primary")

if __name__ == "__main__":
    fix_primary_emails()
