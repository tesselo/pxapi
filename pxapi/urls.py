"""pxapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from pxapi.apiurls import apiurlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "openapi",
        get_schema_view(
            title="Pixels API", description="A pixel grabber engine.", version="1.0.0"
        ),
        name="openapi-schema",
    ),
    path(
        "redoc/",
        TemplateView.as_view(
            template_name="redoc.html", extra_context={"schema_url": "openapi-schema"}
        ),
        name="redoc",
    ),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger.html", extra_context={"schema_url": "openapi-schema"}
        ),
        name="swagger-ui",
    ),
]

urlpatterns += apiurlpatterns
