from django.contrib import admin
from .models import Category, Subcategory, Course, Lesson, Tag, CourseTag

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Tag)
admin.site.register(CourseTag)
