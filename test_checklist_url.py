#!/usr/bin/env python
"""
Script para probar que la URL de checklist funciona correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_checklist_url():
    print("🔍 Probando URL de checklist...")
    
    try:
        # Probar reverse de la URL
        url = reverse('dashboard:checklist')
        print(f"✅ URL de checklist generada correctamente: {url}")
        
        # Probar importación de la vista
        from dashboard.views import checklist_view
        print("✅ Vista checklist_view importada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_checklist_url()
