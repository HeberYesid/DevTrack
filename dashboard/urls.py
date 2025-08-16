from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]
