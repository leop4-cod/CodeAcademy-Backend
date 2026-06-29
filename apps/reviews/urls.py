from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, CertificateViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)
router.register(r'certificates', CertificateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
