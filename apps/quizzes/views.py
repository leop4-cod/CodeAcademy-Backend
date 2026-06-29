from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import EsAdministradorOReadOnly, EsUsuarioAutenticado
from .models import Quiz, Question, Answer, QuizAttempt, QuizAnswer
from .serializers import (
    QuizSerializer, QuestionSerializer, AnswerSerializer,
    QuizAttemptSerializer, QuizAnswerSerializer
)


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
