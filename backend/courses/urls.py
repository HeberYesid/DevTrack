from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubjectViewSet,
    ExerciseViewSet,
    StudentExerciseResultViewSet,
    EnrollmentResultsView,
    MyEnrollmentsView
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'results', StudentExerciseResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
    path('enrollments/<int:pk>/results/', EnrollmentResultsView.as_view({'get': 'list_results'}), name='enrollment-results'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
]
