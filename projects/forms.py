from django import forms

from .models import Project, Stage


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description")


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ("project", "name")


