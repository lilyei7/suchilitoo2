"""
Django URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    return redirect('dashboard:principal')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('cajero/', include('cajero.urls')),
    path('mesero/', include('mesero.urls')),
    path('cocina/', include('cocina.urls', namespace='cocina')),
    path('accounts/', include('accounts.urls')),
    path('rrhh/', include('rrhh.urls')),
    path('', redirect_to_dashboard),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
