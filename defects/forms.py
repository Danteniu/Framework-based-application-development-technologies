from django import forms

from accounts.models import User, UserRole
from projects.models import Project, Stage

from .models import Defect, DefectAttachment, DefectComment, DefectStatus


def _bootstrapify(form: forms.Form) -> None:
    for name, field in form.fields.items():
        widget = field.widget
        cls = widget.attrs.get("class", "")
        if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.URLInput, forms.PasswordInput)):
            widget.attrs["class"] = (cls + " form-control").strip()
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = (cls + " form-control").strip()
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs["class"] = (cls + " form-select").strip()
        elif isinstance(widget, (forms.ClearableFileInput,)):
            widget.attrs["class"] = (cls + " form-control").strip()


class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ("project", "stage", "title", "description", "priority", "assignee", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.all()
        self.fields["stage"].queryset = Stage.objects.select_related("project").all()
        self.fields["assignee"].queryset = User.objects.filter(is_active=True).order_by("username")

        if self.user and getattr(self.user, "role", None) != UserRole.MANAGER:
            # Инженер может создавать/редактировать дефекты, но назначение исполнителя/сроков делает менеджер.
            self.fields.pop("assignee", None)
            self.fields.pop("due_date", None)

        _bootstrapify(self)


class CommentForm(forms.ModelForm):
    class Meta:
        model = DefectComment
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = DefectAttachment
        fields = ("file",)

    def clean_file(self):
        f = self.cleaned_data["file"]
        max_size = 10 * 1024 * 1024  # 10 MB
        if f.size > max_size:
            raise forms.ValidationError("Файл слишком большой (максимум 10 МБ).")
        return f

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)


class StatusChangeForm(forms.Form):
    status = forms.ChoiceField(choices=DefectStatus.choices, label="Новый статус")
    comment = forms.CharField(
        required=False,
        label="Комментарий",
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify(self)


