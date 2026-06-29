from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import EsAdministrador, EsLecturaPublicaEscrituraAuth
from .models import Review, Certificate
from .serializers import ReviewSerializer, CertificateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (EsLecturaPublicaEscrituraAuth,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'student']
    search_fields = ['comment']
    ordering_fields = ['rating', 'created_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = (EsAdministrador,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course']
    ordering_fields = ['issued_at']
