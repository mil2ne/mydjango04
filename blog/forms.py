from django import forms

from core.forms.widgets import HorizontalRadioSelect
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["message", "rating"]
        # widgets = {"rating": forms.Select(choices=[(i, i) for i in range(1, 6)])}
        # widgets = {"rating": forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])}
        widgets = {
            "rating": HorizontalRadioSelect(choices=[(i, i) for i in range(1, 6)])
        }
