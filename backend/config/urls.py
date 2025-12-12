from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """Simple health check for Railway - no DB required"""
    return HttpResponse("OK", content_type="text/plain", status=200)


def home_view(request):
    """Vista de bienvenida para la API"""
    return JsonResponse({
        'message': '🎓 Bienvenido a DevTrack API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'health': '/health/',
            'authentication': '/api/auth/',
            'courses': '/api/courses/',
            'notifications': '/api/notifs/',
            'messaging': '/api/messaging/',
            'admin_panel': '/admin/',
            'api_documentation': '/api/docs/',
            'api_schema': '/api/schema/',
        },
        'documentation': 'https://devtrack-production-2b1d.up.railway.app/api/docs/',
        'description': 'Sistema de gestión educativa para rastrear el progreso académico de estudiantes'
    })


urlpatterns = [
    path('health/', health_check, name='health'),  # Railway health check
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),

    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Apps
    path('api/auth/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/notifs/', include('notifications.urls')),
    path('api/messaging/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
