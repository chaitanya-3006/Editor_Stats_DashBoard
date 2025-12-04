from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import path, reverse

from .views import editor_stats_dashboard, export_csv


# Register Admin URLs
@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path("editor-stats/", editor_stats_dashboard, name="editor_stats_dashboard"),
        path("editor-stats/export/", export_csv, name="editor_stats_export"),
    ]


# Add Sidebar Menu Item
@hooks.register('register_admin_menu_item')
def register_editor_stats_menu_item():
    return MenuItem(
        "Editor Stats",
        reverse("editor_stats_dashboard"),
        icon_name="group",     
        order=200,
    )
