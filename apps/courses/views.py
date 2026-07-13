from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import EsAdministradorOReadOnly, EsAdministrador
from .models import Category, Subcategory, Course, Lesson, Tag, CourseTag
from .serializers import (
    CategorySerializer, SubcategorySerializer, CourseSerializer,
    LessonSerializer, TagSerializer, CourseTagSerializer,
    CourseImageUploadSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    ordering_fields = ['name']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'teacher', 'subcategory']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title']
    ordering_fields = ['order', 'title']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


class CourseTagViewSet(viewsets.ModelViewSet):
    queryset = CourseTag.objects.all()
    serializer_class = CourseTagSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'tag']


class CourseImageUploadView(APIView):
    """
    PUT  /api/courses/{id}/image/  → Sube o reemplaza la imagen del curso.
    DELETE /api/courses/{id}/image/ → Elimina la imagen del curso.
    Solo accesible para staff/profesores (EsAdministrador).
    Acepta multipart/form-data con el campo 'image'.
    Formatos: JPG, PNG, GIF, WEBP, BMP, TIFF. Máximo 5MB.
    Responde: { "detail": "...", "image_url": "https://..." }
    """
    permission_classes = (EsAdministrador,)

    def get_course(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None

    def put(self, request, pk):
        course = self.get_course(pk)
        if course is None:
            return Response({'detail': 'Curso no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseImageUploadSerializer(
            course,
            data=request.data,
            partial=False,
            context={'request': request},
        )
        if serializer.is_valid():
            # Eliminar imagen anterior para no acumular archivos
            if course.image:
                import os
                old_path = course.image.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            serializer.save()
            return Response(
                {
                    'detail': 'Imagen del curso actualizada correctamente.',
                    'image_url': serializer.data.get('image_url'),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Elimina la imagen del curso."""
        course = self.get_course(pk)
        if course is None:
            return Response({'detail': 'Curso no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if course.image:
            import os
            old_path = course.image.path
            if os.path.isfile(old_path):
                os.remove(old_path)
            course.image = None
            course.save(update_fields=['image'])
            return Response({'detail': 'Imagen del curso eliminada.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Este curso no tiene imagen.'}, status=status.HTTP_400_BAD_REQUEST)
