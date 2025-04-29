from drf_yasg import openapi

AUTH_HEADER = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="JWT Token in format: Bearer <token>",
    type=openapi.TYPE_STRING,
    required=True
)