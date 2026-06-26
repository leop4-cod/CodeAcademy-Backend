from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Course(models.Model):
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='courses', on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, related_name='taught_courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', through='CourseTag', related_name='courses')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} - {self.course.title} ({self.rating}/5)"


class Certificate(models.Model):
    student = models.ForeignKey(User, related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    enrollment = models.OneToOneField(
        Enrollment, related_name='certificate', on_delete=models.CASCADE,
        null=True, blank=True
    )
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progress', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.lesson.title}"


class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='quizzes', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    pass_score = models.PositiveIntegerField(default=70)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    student = models.ForeignKey(User, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title}"


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='student_answers', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name='selected', on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"{self.attempt.student.email} - {self.question.text}"


class DiscussionForum(models.Model):
    course = models.ForeignKey(Course, related_name='forums', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class ForumPost(models.Model):
    forum = models.ForeignKey(DiscussionForum, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='forum_posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.forum.title} - {self.title}"


class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='forum_comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.author.email}"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class CourseTag(models.Model):
    course = models.ForeignKey(Course, related_name='course_tags', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name='course_tags', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('course', 'tag')

    def __str__(self):
        return f"{self.course.title} - {self.tag.name}"


class Wishlist(models.Model):
    student = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='wishlist', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"
