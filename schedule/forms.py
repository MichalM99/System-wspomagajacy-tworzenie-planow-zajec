from django import forms
from schedule.models import WeekDay
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
    weekday = forms.IntegerField(widget=forms.Select(choices=DAYS_OF_WEEK))
    HOURS_LIST = generate_hours(15, 8, 10)
    from_hour = forms.TimeField(widget=forms.Select(choices=HOURS_LIST))
    to_hour = forms.TimeField(widget=forms.Select(choices=HOURS_LIST))


