
from django import forms
from django.core.exceptions import ValidationError

from account.models import Profile
from schedule.models import Group, Lecture, Room, Year
from schedule.utils import generate_hours

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

    def clean_year_period(self):
        year_period = self.cleaned_data['year_period']
        first_half = year_period[:4]
        second_half = year_period[5:]
        if not (first_half.isnumeric() and second_half.isnumeric()):
            raise ValidationError("Zły format roku akademickiego!")
        elif int(second_half) - int(first_half) != 1:
            raise ValidationError("Zły format roku akademickiego!")
        elif len(year_period) > 9 or len(year_period) < 9:
            raise ValidationError("Zły format roku akademickiego!")
        elif year_period[4] != '/':
            raise ValidationError("Zły format roku akademickiego!")
        return year_period


class SearchYear(forms.Form):
    query = forms.CharField(label='Kierunek/rok/specjalność:', required=False)


class SearchRoom(forms.Form):
    query = forms.CharField(label='Nazwa/numer sali:', required=False)


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


class AddRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(AddRoomForm, self).__init__(*args, **kwargs)
        self.fields['type_of_lecture'].widget.attrs.update({
            'class': 'form-control-sm'
        })


class EditRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(EditRoomForm, self).__init__(*args, **kwargs)
        self.fields['type_of_lecture'].widget.attrs.update({
            'class': 'form-control-sm'
        })


class AddScheduleForm(forms.Form):
    lecture_unit = forms.IntegerField(max_value=120, min_value=15, label='Długość jednostki godzinowej (w minutach)')
    break_time = forms.IntegerField(max_value=120, min_value=15, label='Minimalna długość przerwy (w minutach)')


class AddScheduleItemForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Grupa',
                                   widget=forms.Select(attrs={'class': 'form-control-sm'}))
    lecture = forms.ModelChoiceField(queryset=Lecture.objects.all(), label='Zajęcia',
                                     widget=forms.Select(attrs={'class': 'form-control-sm'}))
    lecturer = forms.ModelChoiceField(queryset=Profile.objects.all(), label='Prowadzący',
                                      widget=forms.Select(attrs={'class': 'form-control-sm'}))
    lecture_unit = forms.IntegerField(label='Liczba jednostek godzinowych jednorazowo', max_value=10)

    def __init__(self, *args, **kwargs):
        year_id = kwargs.pop('year_id', None)
        super(AddScheduleItemForm, self).__init__(*args, **kwargs)

        if year_id:
            self.fields['group'].queryset = Group.objects.filter(year_id=year_id).order_by('group_number')
            self.fields['lecture'].queryset = Lecture.objects.filter(year_id=year_id).order_by('lecture_name')


class AddRoomToScheduleForm(forms.Form):
    room = forms.ModelChoiceField(queryset=Room.objects.all(), label='Wybierz salę')

    def __init__(self, *args, **kwargs):
        super(AddRoomToScheduleForm, self).__init__(*args, **kwargs)
        self.fields['room'].widget.attrs.update({
            'class': 'form-control-sm'
        })


TYPE_OF_LECTURE = (
    (0, 'Laboratorium'),
    (1, 'Ćwiczenia'),
    (2, 'Wykład'),
)


class AddLectureForm(forms.Form):
    lecture_name = forms.CharField(label='Nazwa zajęć', max_length=100)
    type_of_lecture = forms.IntegerField(label='Rodzaj zajęć', widget=forms.Select(choices=TYPE_OF_LECTURE, attrs={
        'class': 'form-control-sm'
    }))
