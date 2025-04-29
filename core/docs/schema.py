from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

SCHEMA_VIEW = get_schema_view(
    openapi.Info(
        title="Dream Track API",
        default_version='v1',
        description="API documentation for Dream Track application",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="Apache 2.0License"),
    ),
    public=True, #False
    permission_classes=(permissions.AllowAny,),
)