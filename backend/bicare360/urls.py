"""
URL configuration for bicare360 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT Token endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API endpoints
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.patients.urls")),
    path("api/v1/", include("apps.enrollment.urls")),
    path("api/v1/", include("apps.medications.urls")),
    path("api/v1/", include("apps.appointments.urls")),
    path("api/v1/", include("apps.consents.urls")),
    path("api/v1/", include("apps.messaging.urls")),
    path("api/v1/nursing/", include("apps.nursing.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# Debug Toolbar URLs (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
