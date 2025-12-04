from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.http import require_POST

from .models import BlogPage, BlogComment


# --------------------------------------------------------
#   LIKE API
# --------------------------------------------------------
@require_POST
def like_blog(request, page_id):
    """Increase like count for a blog post."""
    blog = get_object_or_404(BlogPage, id=page_id)

    BlogPage.objects.filter(id=page_id).update(
        likes=F("likes") + 1
    )

    blog.refresh_from_db()

    return JsonResponse({
        "success": True,
        "likes": blog.likes
    })


# --------------------------------------------------------
#   COMMENT API
# --------------------------------------------------------
@require_POST
def add_comment(request, page_id):
    """Add a comment to a blog post."""
    blog = get_object_or_404(BlogPage, id=page_id)

    text = request.POST.get("comment", "").strip()

    if not text:
        return JsonResponse({
            "success": False,
            "error": "Comment cannot be empty."
        })

    # Create comment record
    BlogComment.objects.create(
        blog=blog,
        text=text,
        user=request.user if request.user.is_authenticated else None
    )

    # Update comment count
    BlogPage.objects.filter(id=page_id).update(
        comments_count=F("comments_count") + 1
    )

    blog.refresh_from_db()

    return JsonResponse({
        "success": True,
        "comment": text,
        "comments_count": blog.comments_count
    })


# --------------------------------------------------------
#   OPTIONAL: LIST VIEW 
# --------------------------------------------------------
def blog_list(request):
    """Simple public blog list page."""
    blogs = BlogPage.objects.live().order_by("-last_published_at")

    return render(request, "blog/blog_list.html", {
        "blogs": blogs
    })


# --------------------------------------------------------
#   OPTIONAL: FETCH COMMENTS API (AJAX)
# --------------------------------------------------------
def get_comments(request, page_id):
    """Return all comments for a blog as JSON."""
    blog = get_object_or_404(BlogPage, id=page_id)

    comments = blog.comments.order_by("-created_at").values(
        "text", "created_at"
    )

    return JsonResponse(list(comments), safe=False)
