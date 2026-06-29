from django.contrib import admin
from .models import DiscussionForum, ForumPost, ForumComment

admin.site.register(DiscussionForum)
admin.site.register(ForumPost)
admin.site.register(ForumComment)
