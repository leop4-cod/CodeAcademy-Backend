from django.contrib import admin
from .models import User, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_teacher', 'is_student', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_teacher', 'is_student', 'is_staff')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at',)
