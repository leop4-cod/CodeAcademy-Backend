from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet, QuestionViewSet, AnswerViewSet,
    QuizAttemptViewSet, QuizAnswerViewSet
)

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'quiz-answers', QuizAnswerViewSet, basename='quiz-answer')

urlpatterns = [
    path('', include(router.urls)),
]
