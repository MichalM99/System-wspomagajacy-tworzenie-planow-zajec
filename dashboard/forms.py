from django import forms


class AddNewsForm(forms.Form):
    """Form that allows to add news."""

    headline = forms.CharField(max_length=100, label='Tytuł')
    content = forms.CharField(widget=forms.Textarea, label='Treść')