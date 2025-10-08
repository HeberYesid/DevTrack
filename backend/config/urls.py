from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def home_view(request):
    """Vista de bienvenida para la API"""
    return JsonResponse({
        'message': '🎓 Bienvenido a DevTrack API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'authentication': '/api/auth/',
            'courses': '/api/courses/',
            'notifications': '/api/notifs/',
            'admin_panel': '/admin/',
            'api_documentation': '/api/docs/',
            'api_schema': '/api/schema/',
        },
        'documentation': 'http://localhost:8000/api/docs/',
        'description': 'Sistema de gestión educativa para rastrear el progreso académico de estudiantes'
    })


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),

    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Apps
    path('api/auth/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/notifs/', include('notifications.urls')),
]
