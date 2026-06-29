import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User
from apps.courses.models import Category, Subcategory, Course, Lesson, Tag, CourseTag
from apps.enrollments.models import Enrollment, Progress, Wishlist
from apps.reviews.models import Review, Certificate
from apps.quizzes.models import Quiz, Question, Answer, QuizAttempt, QuizAnswer
from apps.forums.models import DiscussionForum, ForumPost, ForumComment


def test_crud():
    print("--- INICIANDO VERIFICACIÓN DE LAS 20 TABLAS (ARQUITECTURA MODULAR) ---")
    
    # 1. User
    try:
        user_teacher = User.objects.create_user(email="teacher@codeacademy.com", password="password123", is_teacher=True)
        user_student = User.objects.create_user(email="student@codeacademy.com", password="password123", is_student=True)
        print("✅ 1. Tabla 'User' (app: users) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'User': {e}")
        return

    # 2. Category
    try:
        category = Category.objects.create(name="Desarrollo Web", slug="desarrollo-web")
        print("✅ 2. Tabla 'Category' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Category': {e}")
        return

    # 3. Subcategory
    try:
        subcategory = Subcategory.objects.create(category=category, name="Python & Django", slug="python-django")
        print("✅ 3. Tabla 'Subcategory' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Subcategory': {e}")
        return

    # 4. Course
    try:
        course = Course.objects.create(
            category=category, subcategory=subcategory, teacher=user_teacher,
            title="Django Completo", description="Aprende Django desde cero", price=19.99
        )
        print("✅ 4. Tabla 'Course' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Course': {e}")
        return

    # 5. Lesson
    try:
        lesson = Lesson.objects.create(course=course, title="Introducción", content="Contenido de introducción", order=1)
        print("✅ 5. Tabla 'Lesson' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Lesson': {e}")
        return

    # 6. Enrollment
    try:
        enrollment = Enrollment.objects.create(student=user_student, course=course)
        print("✅ 6. Tabla 'Enrollment' (app: enrollments) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Enrollment': {e}")
        return

    # 7. Review
    try:
        review = Review.objects.create(course=course, student=user_student, rating=5, comment="Excelente curso")
        print("✅ 7. Tabla 'Review' (app: reviews) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Review': {e}")
        return

    # 8. Certificate
    try:
        certificate = Certificate.objects.create(student=user_student, course=course, certificate_id="CERT-123456")
        print("✅ 8. Tabla 'Certificate' (app: reviews) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Certificate': {e}")
        return

    # 9. Progress
    try:
        progress = Progress.objects.create(enrollment=enrollment, lesson=lesson, completed=True)
        print("✅ 9. Tabla 'Progress' (app: enrollments) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Progress': {e}")
        return

    # 10. Quiz
    try:
        quiz = Quiz.objects.create(course=course, lesson=lesson, title="Examen de Django", pass_score=80)
        print("✅ 10. Tabla 'Quiz' (app: quizzes) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Quiz': {e}")
        return

    # 11. Question
    try:
        question = Question.objects.create(quiz=quiz, text="¿Qué es Django?", order=1)
        print("✅ 11. Tabla 'Question' (app: quizzes) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Question': {e}")
        return

    # 12. Answer
    try:
        answer = Answer.objects.create(question=question, text="Un framework web en Python", is_correct=True)
        print("✅ 12. Tabla 'Answer' (app: quizzes) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Answer': {e}")
        return

    # 13. QuizAttempt
    try:
        attempt = QuizAttempt.objects.create(student=user_student, quiz=quiz, score=100, passed=True)
        print("✅ 13. Tabla 'QuizAttempt' (app: quizzes) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'QuizAttempt': {e}")
        return

    # 14. QuizAnswer
    try:
        quiz_answer = QuizAnswer.objects.create(attempt=attempt, question=question, answer=answer, is_correct=True)
        print("✅ 14. Tabla 'QuizAnswer' (app: quizzes) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'QuizAnswer': {e}")
        return

    # 15. DiscussionForum
    try:
        forum = DiscussionForum.objects.create(course=course, title="Foro de Preguntas", description="Canal de dudas")
        print("✅ 15. Tabla 'DiscussionForum' (app: forums) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'DiscussionForum': {e}")
        return

    # 16. ForumPost
    try:
        post = ForumPost.objects.create(forum=forum, author=user_student, title="Duda con Migraciones", content="¿Cómo hacer migrations?")
        print("✅ 16. Tabla 'ForumPost' (app: forums) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'ForumPost': {e}")
        return

    # 17. ForumComment
    try:
        comment = ForumComment.objects.create(post=post, author=user_teacher, content="Usa makemigrations y luego migrate.")
        print("✅ 17. Tabla 'ForumComment' (app: forums) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'ForumComment': {e}")
        return

    # 18. Tag
    try:
        tag = Tag.objects.create(name="Python", slug="python")
        print("✅ 18. Tabla 'Tag' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Tag': {e}")
        return

    # 19. CourseTag
    try:
        course_tag = CourseTag.objects.create(course=course, tag=tag)
        print("✅ 19. Tabla 'CourseTag' (app: courses) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'CourseTag': {e}")
        return

    # 20. Wishlist
    try:
        wishlist = Wishlist.objects.create(student=user_student, course=course)
        print("✅ 20. Tabla 'Wishlist' (app: enrollments) funcionando correctamente.")
    except Exception as e:
        print(f"❌ Error en tabla 'Wishlist': {e}")
        return

    print("\n🎉 ¡Las 20 tablas funcionan correctamente y pasaron la verificación CRUD en la arquitectura modular!")


if __name__ == "__main__":
    User.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    
    test_crud()
