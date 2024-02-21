"""
URL configuration for resturantBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.conf import settings
from django.conf.urls.static import static
from core.views import UserViewSet
from rest_framework import routers
from djoser import views as djoser_views
from core.views import OTPView, ExcelExportView

admin.site.site_header = 'Storefront Admin'
admin.site.index_title = 'Admin'

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path("adminPanel/", admin.site.urls),
    path("admin/", include('core.urls')),
    path("user/", include('client.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/otp', OTPView.as_view(), name='otp_view'),
    path('admin/users/', UserViewSet.as_view({'get': 'list'}), name='user-detail'),
    path('admin/orderExcel',
         ExcelExportView.as_view(),
         name='excel-export')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
