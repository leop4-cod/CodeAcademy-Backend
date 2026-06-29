from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscussionForumViewSet, ForumPostViewSet, ForumCommentViewSet

router = DefaultRouter()
router.register(r'discussion-forums', DiscussionForumViewSet, basename='discussion-forum')
router.register(r'forum-posts', ForumPostViewSet, basename='forum-post')
router.register(r'forum-comments', ForumCommentViewSet, basename='forum-comment')

urlpatterns = [
    path('', include(router.urls)),
]
