# blog/models.py

from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from django.db.models import F


class BlogPage(Page):
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    body = RichTextField(blank=True)

    # Analytics fields
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    content_panels = Page.content_panels + [
        FieldPanel("cover_image"),
        FieldPanel("body"),
    ]

    def serve(self, request):
        """Auto-increment views for analytics."""
        BlogPage.objects.filter(id=self.id).update(
            views=F("views") + 1
        )
        return super().serve(request)


class BlogComment(models.Model):
    blog = models.ForeignKey(BlogPage, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment on {self.blog.title}"
