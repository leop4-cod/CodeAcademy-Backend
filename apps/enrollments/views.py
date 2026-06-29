from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import EsUsuarioAutenticado
from .models import Enrollment, Progress, Wishlist
from .serializers import EnrollmentSerializer, ProgressSerializer, WishlistSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'student']
    ordering_fields = ['enrolled_at']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.groups.filter(name='Administrador').exists():
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['enrollment', 'lesson', 'completed']
    ordering_fields = ['completed_at']


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['added_at']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.groups.filter(name='Administrador').exists():
            return Wishlist.objects.all()
        return Wishlist.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
