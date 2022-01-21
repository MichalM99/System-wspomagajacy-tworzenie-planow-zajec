from django import forms


class AddNewsForm(forms.Form):
    headline = forms.CharField(max_length=100, label='Tytuł')
    content = forms.CharField(widget=forms.Textarea, label='Treść')