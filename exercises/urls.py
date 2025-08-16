from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.home, name='home'),
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/<int:exercise_id>/submit/', views.submit_exercise, name='submit_exercise'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/exercise-stats/', views.exercise_stats_api, name='exercise_stats_api'),
]
