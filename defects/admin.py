from django.contrib import admin

from .models import Defect, DefectAttachment, DefectComment, DefectHistory


class DefectAttachmentInline(admin.TabularInline):
    model = DefectAttachment
    extra = 0


class DefectCommentInline(admin.TabularInline):
    model = DefectComment
    extra = 0


class DefectHistoryInline(admin.TabularInline):
    model = DefectHistory
    extra = 0
    readonly_fields = ("actor", "action", "from_status", "to_status", "changes", "created_at")
    can_delete = False


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "stage", "status", "priority", "assignee", "due_date", "created_at")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description")
    inlines = [DefectAttachmentInline, DefectCommentInline, DefectHistoryInline]


