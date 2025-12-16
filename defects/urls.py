from django.urls import path

from . import views

app_name = "defects"

urlpatterns = [
    path("", views.list_defects, name="list"),
    path("defects/create/", views.create_defect, name="create"),
    path("defects/<int:defect_id>/", views.defect_detail, name="detail"),
    path("defects/<int:defect_id>/edit/", views.edit_defect, name="edit"),
    path("defects/<int:defect_id>/comment/", views.add_comment, name="comment"),
    path("defects/<int:defect_id>/attach/", views.add_attachment, name="attach"),
    path("defects/<int:defect_id>/status/", views.change_status, name="status"),
]


