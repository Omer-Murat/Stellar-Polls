from django import forms
from .models import Question

class PollForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Başlangıç Tarihi ve Saati"
    )

    class Meta:
        model = Question
        fields = ['question_text', 'start_date', 'end_date', 'is_public']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
