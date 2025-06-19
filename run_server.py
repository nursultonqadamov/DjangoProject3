#!/usr/bin/env python
"""
Replit uchun server ishga tushirish fayli
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject3.settings')
    
    # Migratsiyalarni avtomatik bajarish
    try:
        django.setup()
        from django.core.management import call_command
        
        print("🔄 Migratsiyalar bajarilmoqda...")
        call_command('makemigrations')
        call_command('migrate')
        
        # Superuser yaratish (agar yo'q bo'lsa)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            print("👤 Admin foydalanuvchi yaratilmoqda...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ Admin yaratildi: username=admin, password=admin123")
        
        print("🚀 Server ishga tushirilmoqda...")
        
    except Exception as e:
        print(f"⚠️ Xatolik: {e}")
    
    # Serverni ishga tushirish
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
