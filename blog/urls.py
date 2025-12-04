# blog/urls.py

from django.urls import path
from .views import like_blog, add_comment, get_comments, blog_list

urlpatterns = [
    path("", blog_list, name="blog_list"),
    path("like/<int:page_id>/", like_blog, name="like_blog"),
    path("comment/<int:page_id>/", add_comment, name="add_comment"),
    path("comments/<int:page_id>/", get_comments, name="get_comments"),
]
