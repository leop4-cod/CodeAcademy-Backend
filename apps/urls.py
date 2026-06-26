from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import TokenPersonalizadoSerializer
from .views import (
    RegisterView, UserViewSet, CategoryViewSet, SubcategoryViewSet, CourseViewSet, LessonViewSet,
    EnrollmentViewSet, ReviewViewSet, CertificateViewSet, ProgressViewSet,
    QuizViewSet, QuestionViewSet, AnswerViewSet, QuizAttemptViewSet, QuizAnswerViewSet,
    DiscussionForumViewSet, ForumPostViewSet, ForumCommentViewSet,
    TagViewSet, CourseTagViewSet, WishlistViewSet
)


class LoginView(TokenObtainPairView):
    serializer_class = TokenPersonalizadoSerializer


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'reviews', ReviewViewSet)
router.register(r'certificates', CertificateViewSet)
router.register(r'progress', ProgressViewSet, basename='progress')
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'quiz-answers', QuizAnswerViewSet, basename='quiz-answer')
router.register(r'discussion-forums', DiscussionForumViewSet, basename='discussion-forum')
router.register(r'forum-posts', ForumPostViewSet, basename='forum-post')
router.register(r'forum-comments', ForumCommentViewSet, basename='forum-comment')
router.register(r'tags', TagViewSet)
router.register(r'course-tags', CourseTagViewSet)
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
