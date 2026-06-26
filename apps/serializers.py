from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group
from .models import (
    User, Category, Subcategory, Course, Lesson,
    Enrollment, Review, Certificate, Progress,
    Quiz, Question, Answer, QuizAttempt, QuizAnswer,
    DiscussionForum, ForumPost, ForumComment,
    Tag, CourseTag, Wishlist
)


class TokenPersonalizadoSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_teacher', 'is_student', 'bio', 'avatar', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo electrónico.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        grupo_usuario, _ = Group.objects.get_or_create(name='Usuario')
        user.groups.add(grupo_usuario)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'price', 'image', 'category', 'subcategory',
            'category_name', 'teacher', 'lessons', 'created_at', 'is_published'
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'enrolled_at', 'completed_at')
        read_only_fields = ('student',)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('student',)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La calificación debe estar entre 1 y 5.')
        return value


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = '__all__'


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = '__all__'
        read_only_fields = ('student',)


class DiscussionForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionForum
        fields = '__all__'


class ForumPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = '__all__'
        read_only_fields = ('author',)


class ForumCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumComment
        fields = '__all__'
        read_only_fields = ('author',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CourseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTag
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Wishlist
        fields = ('id', 'student', 'course', 'course_title', 'added_at')
        read_only_fields = ('student',)
