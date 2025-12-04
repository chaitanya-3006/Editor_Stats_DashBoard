from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from wagtail.models import Page
import csv
from datetime import datetime

User = get_user_model()


# -----------------------------
#   MAIN DASHBOARD VIEW
# -----------------------------
def editor_stats_dashboard(request):

    # ---------------------------
    #  FILTERS
    # ---------------------------
    author_filter = request.GET.get("author")
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    pages = Page.objects.all().specific()

    if author_filter:
        pages = pages.filter(owner_id=author_filter)

    if start_date:
        pages = pages.filter(last_published_at__date__gte=start_date)

    if end_date:
        pages = pages.filter(last_published_at__date__lte=end_date)

    # ---------------------------
    #  METRICS
    # ---------------------------
    total_drafts = pages.filter(live=False, has_unpublished_changes=True).count()
    total_published = pages.filter(live=True).count()
    scheduled = pages.filter(go_live_at__isnull=False, live=False).count()

    # Stale pages = not updated for 60+ days
    stale_days = now() - timedelta(days=60)
    stale_pages = pages.filter(latest_revision_created_at__lt=stale_days).count()

    # ---------------------------
    #  CHART DATA (daily)
    # ---------------------------
    labels = []
    views_data = []
    likes_data = []
    comments_data = []

    for i in range(7):
        day = now().date() - timedelta(days=i)
        labels.append(day.strftime("%b %d"))

    # Get pages updated on this day
        day_pages = pages.filter(latest_revision_created_at__date=day)

        total_views = sum(getattr(p, "views", 0) for p in day_pages)
        total_likes = sum(getattr(p, "likes", 0) for p in day_pages)
        total_comments = sum(getattr(p, "comments_count", 0) for p in day_pages)

        views_data.append(total_views)
        likes_data.append(total_likes)
        comments_data.append(total_comments)

    labels.reverse()
    views_data.reverse()
    likes_data.reverse()
    comments_data.reverse()


    # ---------------------------
    #  TABLE DATA
    # ---------------------------
    table = []

    for p in pages[:50]:  # limit 50 rows
        table.append({
            "title": p.title,
            "views": getattr(p, "views", 0),
            "likes": getattr(p, "likes", 0),
            "comments": getattr(p, "comments_count", 0),
            "updated_at": p.latest_revision_created_at,
        })

    # ---------------------------
    #  CONTEXT
    # ---------------------------
    context = {
        "authors": User.objects.all(),
        "total_drafts": total_drafts,
        "total_published": total_published,
        "scheduled": scheduled,
        "stale_pages": stale_pages,

        "labels": labels,
        "views": views_data,
        "likes": likes_data,
        "comments": comments_data,

        "table": table,
    }

    return render(request, "dashboard/stats.html", context)


# -----------------------------
#   CSV EXPORT VIEW
# -----------------------------
def export_csv(request):
    pages = Page.objects.all().specific()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=editor_stats.csv"

    writer = csv.writer(response)
    writer.writerow(["Title", "Views", "Likes", "Comments", "Updated"])

    for p in pages:
        writer.writerow([
            p.title,
            getattr(p, "views", 0),
            getattr(p, "likes", 0),
            getattr(p, "comments_count", 0),
            p.latest_revision_created_at,
        ])

    return response

