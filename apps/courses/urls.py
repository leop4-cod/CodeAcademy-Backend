from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SubcategoryViewSet, CourseViewSet,
    LessonViewSet, TagViewSet, CourseTagViewSet,
    CourseImageUploadView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'tags', TagViewSet)
router.register(r'course-tags', CourseTagViewSet)

urlpatterns = [
    path('courses/<int:pk>/image/', CourseImageUploadView.as_view(), name='course-image-upload'),
    path('', include(router.urls)),
]
