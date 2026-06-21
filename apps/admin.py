from django.contrib import admin
from .models import (
    User, Category, Subcategory, Course, Lesson,
    Enrollment, Review, Certificate, Progress,
    Quiz, Question, Answer, QuizAttempt, QuizAnswer,
    DiscussionForum, ForumPost, ForumComment,
    Tag, CourseTag, Wishlist
)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(Review)
admin.site.register(Certificate)
admin.site.register(Progress)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizAttempt)
admin.site.register(QuizAnswer)
admin.site.register(DiscussionForum)
admin.site.register(ForumPost)
admin.site.register(ForumComment)
admin.site.register(Tag)
admin.site.register(CourseTag)
admin.site.register(Wishlist)
