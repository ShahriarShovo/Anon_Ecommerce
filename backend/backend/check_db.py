#!/usr/bin/env python
"""
Simple database check for email settings
"""

import sqlite3
import os

def check_email_database():
    print("🔍 Checking Email Settings Database")
    print("=" * 40)
    
    try:
        # Connect to database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if email settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%email%'")
        email_tables = cursor.fetchall()
        print(f"📊 Email-related tables: {email_tables}")
        
        # Check settings_emailsettings table specifically
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings_emailsettings'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ settings_emailsettings table exists")
            
            # Get count
            cursor.execute("SELECT COUNT(*) FROM settings_emailsettings")
            count = cursor.fetchone()[0]
            print(f"📊 Total email settings: {count}")
            
            if count > 0:
                # Get all email settings
                cursor.execute("SELECT id, name, email_address, smtp_host, is_active, is_primary, created_at FROM settings_emailsettings")
                settings = cursor.fetchall()
                
                print("\n📧 Email Settings Found:")
                print("-" * 50)
                for setting in settings:
                    print(f"ID: {setting[0]}")
                    print(f"Name: {setting[1]}")
                    print(f"Email: {setting[2]}")
                    print(f"SMTP Host: {setting[3]}")
                    print(f"Active: {setting[4]}")
                    print(f"Primary: {setting[5]}")
                    print(f"Created: {setting[6]}")
                    print("-" * 50)
                
                print(f"\n✅ Database has {count} email settings")
                print("   The email selection system should work!")
            else:
                print("\n⚠️  No email settings found in database")
                print("   This explains why you see 'No Email Settings Found'")
        else:
            print("❌ settings_emailsettings table does NOT exist")
            print("   Run migrations first: python manage.py makemigrations && python manage.py migrate")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_email_database()
