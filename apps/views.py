from rest_framework import viewsets, permissions, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from .models import (
    User, Category, Subcategory, Course, Lesson,
    Enrollment, Review, Certificate, Progress,
    Quiz, Question, Answer, QuizAttempt, QuizAnswer,
    DiscussionForum, ForumPost, ForumComment,
    Tag, CourseTag, Wishlist
)
from .serializers import (
    UserSerializer, CategorySerializer, SubcategorySerializer, CourseSerializer, LessonSerializer,
    EnrollmentSerializer, ReviewSerializer, CertificateSerializer, ProgressSerializer,
    QuizSerializer, QuestionSerializer, AnswerSerializer, QuizAttemptSerializer, QuizAnswerSerializer,
    DiscussionForumSerializer, ForumPostSerializer, ForumCommentSerializer,
    TagSerializer, CourseTagSerializer, WishlistSerializer
)
from .permissions import EsAdministradorOReadOnly, EsAdministrador, EsUsuarioAutenticado, EsLecturaPublicaEscrituraAuth


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (EsAdministrador,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name']


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


class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['enrollment', 'lesson', 'completed']
    ordering_fields = ['completed_at']


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson']
    search_fields = ['title']
    ordering_fields = ['title']


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['quiz']
    ordering_fields = ['order']


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['question']
    search_fields = ['text']


class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'quiz']
    ordering_fields = ['started_at', 'score']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.groups.filter(name='Administrador').exists():
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class QuizAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuizAnswer.objects.all()
    serializer_class = QuizAnswerSerializer
    permission_classes = (EsUsuarioAutenticado,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['attempt', 'question']


class DiscussionForumViewSet(viewsets.ModelViewSet):
    queryset = DiscussionForum.objects.all()
    serializer_class = DiscussionForumSerializer
    permission_classes = (EsAdministradorOReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title']
    ordering_fields = ['created_at']


class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    permission_classes = (EsLecturaPublicaEscrituraAuth,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['forum', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ForumCommentViewSet(viewsets.ModelViewSet):
    queryset = ForumComment.objects.all()
    serializer_class = ForumCommentSerializer
    permission_classes = (EsLecturaPublicaEscrituraAuth,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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


def home_view(request):
    return render(request, 'index.html')
