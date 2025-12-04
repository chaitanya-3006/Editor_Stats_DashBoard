from django.urls import path
from .views import editor_stats_dashboard,export_csv

urlpatterns = [
    path("", editor_stats_dashboard, name="editor_stats_dashboard"),
    path("export/", export_csv, name="dashboard_export_csv"),
]
