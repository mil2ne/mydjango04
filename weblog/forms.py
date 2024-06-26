from django import forms

from core.forms.widgets import (
    CounterTextInput,
    IosSwitchInput,
    PreviewClearableFileInput,
)
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "status", "photo", "tag_set", "is_public"]
        widgets = {
            "title": CounterTextInput,
            "is_public": IosSwitchInput,
            "photo": PreviewClearableFileInput,
        }


class ConfirmDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label="동의",
        help_text="삭제에 동의하시면 체크하세요",
        required=True,
        error_messages={"required": "동의하지 않으면 삭제할 수 없습니다."},
    )
