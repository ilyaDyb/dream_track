"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from core.docs.schema import SCHEMA_VIEW
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #admin
    path('admin/', admin.site.urls),
    
    # api
    path('api/', include('core.authentication.urls')),
    path('api/', include('core.dream.urls')),
    path('api/', include('core.finance.urls')),
    path('api/', include('core.accounts.urls')),
    path('api/', include('core.todo.urls')),
    path('api/', include('core.shop.urls')),
    
    # docs
    path('swagger/', SCHEMA_VIEW.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', SCHEMA_VIEW.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)