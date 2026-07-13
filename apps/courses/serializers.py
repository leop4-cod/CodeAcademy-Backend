from rest_framework import serializers
from .models import Category, Subcategory, Course, Lesson, Tag, CourseTag

# Mismos límites que el avatar de usuario
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff']
MAX_IMAGE_SIZE_MB = 5


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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'price', 'image', 'image_url', 'category', 'subcategory',
            'category_name', 'teacher', 'lessons', 'created_at', 'is_published'
        )
        extra_kwargs = {'image': {'required': False, 'allow_null': True}}

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CourseImageUploadSerializer(serializers.ModelSerializer):
    """Serializer dedicado para subir/reemplazar la imagen de un curso (solo staff)."""
    image = serializers.ImageField(required=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('image', 'image_url')

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_image(self, value):
        # Validar tamaño máximo
        max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f'La imagen es demasiado grande. El tamaño máximo es {MAX_IMAGE_SIZE_MB}MB.'
            )
        # Validar tipo MIME
        content_type = getattr(value, 'content_type', '')
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError(
                'Formato no soportado. Use JPG, PNG, GIF, WEBP, BMP o TIFF.'
            )
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CourseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTag
        fields = '__all__'
