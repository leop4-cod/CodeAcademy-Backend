from rest_framework import serializers
from .models import Enrollment, Progress, Wishlist


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'enrolled_at', 'completed_at')
        read_only_fields = ('student',)


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Wishlist
        fields = ('id', 'student', 'course', 'course_title', 'added_at')
        read_only_fields = ('student',)
