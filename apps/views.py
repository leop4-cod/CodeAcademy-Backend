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


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_teacher


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'teacher', 'subcategory']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = (permissions.IsAdminUser,)


class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enrollment']


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'lesson']


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']


class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'quiz']

    def get_queryset(self):
        if self.request.user.is_staff:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class QuizAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuizAnswer.objects.all()
    serializer_class = QuizAnswerSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['attempt']


class DiscussionForumViewSet(viewsets.ModelViewSet):
    queryset = DiscussionForum.objects.all()
    serializer_class = DiscussionForumSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']


class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['forum']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ForumCommentViewSet(viewsets.ModelViewSet):
    queryset = ForumComment.objects.all()
    serializer_class = ForumCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CourseTagViewSet(viewsets.ModelViewSet):
    queryset = CourseTag.objects.all()
    serializer_class = CourseTagSerializer
    permission_classes = (IsTeacherOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'tag']


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Wishlist.objects.all()
        return Wishlist.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


def home_view(request):
    return render(request, 'index.html')
