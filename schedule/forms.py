from django import forms
from schedule.models import Year, Group
from schedule.utils import generate_hours
import datetime as dt


DAYS_OF_WEEK = (
    (0, 'Poniedziałek'),
    (1, 'Wtorek'),
    (2, 'Środa'),
    (3, 'Czwartek'),
    (4, 'Piątek'),
    (5, 'Sobota'),
    (6, 'Niedziela'),
)

class AddAvailabilityForm(forms.Form):
    weekday = forms.IntegerField(widget=forms.Select(choices=DAYS_OF_WEEK, attrs={
        'class': 'form-control-sm'
    }))
    HOURS_LIST = generate_hours(15, 8, 22)
    from_hour = forms.TimeField(widget=forms.Select(choices=HOURS_LIST, attrs={
        'class': 'form-control-sm'
    }))
    to_hour = forms.TimeField(widget=forms.Select(choices=HOURS_LIST, attrs={
        'class': 'form-control-sm'
    }))


SEMESTER_CHOICES = (
    ('letni', 'letni'),
    ('zimowy', 'zimowy'),
)

TYPE_OF_STUDIES = (
    ('stacjonarne', 'stacjonarne'),
    ('niestacjonarne', 'niestacjonarne'),
)


class AddYear(forms.Form):
    year_name = forms.CharField(max_length=100, label='Nazwa kierunku')
    speciality = forms.CharField(max_length=50, label='Specjalność')
    year_period = forms.CharField(max_length=9, label='Rok akademicki (yyyy/yyyy)')
    type_of_studies = forms.CharField(label='Tok studiów', widget=forms.Select(choices=TYPE_OF_STUDIES, attrs={
        'class': 'form-control-sm'
    }))
    type_of_semester = forms.CharField(label='Rodzaj semestru', widget=forms.Select(choices=SEMESTER_CHOICES, attrs={
        'class': 'form-control-sm'
    }))



class AddGroup(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('year', 'quantity', 'group_number')


class SearchYear(forms.Form):
    query = forms.CharField(label='Kierunek/rok/specjalność:')


class ManageYearForm(forms.ModelForm):
    class Meta:
        model = Year
        fields = ('year_name', 'speciality', 'year_period', 'type_of_studies', 'type_of_semester')
        widgets = {
            'type_of_studies': forms.Select(choices=TYPE_OF_STUDIES, attrs={'class': 'form-control-sm'}),
            'type_of_semester': forms.Select(choices=SEMESTER_CHOICES, attrs={'class': 'form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super(ManageYearForm, self).__init__(*args, **kwargs)
        self.fields['type_of_studies'].widget.attrs.update({
            'class': 'form-control-sm'
        })
        self.fields['type_of_semester'].widget.attrs.update({
             'class': 'form-control-sm'
        })


class AddGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ('year',)