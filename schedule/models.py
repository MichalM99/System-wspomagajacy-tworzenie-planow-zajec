from django.db import models
from django.contrib.auth.models import User
from account.models import Profile
import datetime as dt

class Schedule(models.Model):
    schedule_name = models.CharField(verbose_name='nazwa planu', max_length=100)
    class Meta:


        verbose_name = 'plan'
        verbose_name_plural = 'plany'


class Year(models.Model):
    year_name = models.CharField(verbose_name='kierunek', max_length=100)
    speciality = models.CharField(verbose_name='Specjalność', max_length=50)
    year_period = models.CharField(verbose_name='Rok akademicki (yyyy/yyyy)', max_length=9,
                                   default=str((dt.datetime.now() - dt.timedelta(days=365)).year) + '/' + str(dt.datetime.now().year))
    type_of_semester = models.CharField(max_length=100, default='letni', verbose_name='Rodzaj semestru')
    type_of_studies = models.CharField(max_length=100, default='stacjonarne', verbose_name='Tok studiów')

    class Meta:
        verbose_name = 'rok'
        verbose_name_plural = 'kierunki'

    def __str__(self):
        return self.year_name + ' ' +  self.year_period + ' ' + self.type_of_semester + ' ' + self.type_of_studies


class Group(models.Model):
    year = models.ForeignKey(Year, models.CASCADE)
    quantity = models.IntegerField(verbose_name='liczebność grupy')
    group_number = models.IntegerField(verbose_name='numer grupy')


    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'

    def __str__(self):
        return self.year.year_name + ', grupa nr ' + str(self.group_number) + ', liczebność: ' + str(self.quantity)


class Lecture(models.Model):
    lecture_name = models.CharField(verbose_name='nazwa zajęć', max_length=100)


class ScheduleItem(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    from_hour = models.TimeField()
    to_hour = models.TimeField()


    class Meta:
        verbose_name = 'pozycja planu'


class Room(models.Model):
    room_name = models.CharField(verbose_name='nazwa sali', max_length=100)
    capacity = models.IntegerField()
    description = models.TextField(verbose_name='opis sali', max_length=255)


    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'


class RoomItem(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)


class LecturerItem(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)


DAYS_OF_WEEK = (
    (0, 'Poniedziałek'),
    (1, 'Wtorek'),
    (2, 'Środa'),
    (3, 'Czwartek'),
    (4, 'Piątek'),
    (5, 'Sobota'),
    (6, 'Niedziela'),
)


class WeekDay(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return DAYS_OF_WEEK[self.weekday][1]


class LecturerAvailability(models.Model):
    weekday = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    from_hour = models.TimeField(default=dt.time(00, 00))
    to_hour = models.TimeField(default=dt.time(00, 00))
