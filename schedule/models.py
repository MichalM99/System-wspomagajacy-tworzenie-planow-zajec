from django.db import models
from account.models import Profile


class Schedule(models.Model):
    schedule_name = models.CharField(verbose_name='nazwa planu', max_length=100)
    class Meta:


        verbose_name = 'plan'
        verbose_name_plural = 'plany'


class Year(models.Model):
    year_name = models.CharField(verbose_name='kierunek', max_length=100)


    class Meta:
        verbose_name = 'rok'


class Group(models.Model):
    year = models.ForeignKey(Year, models.CASCADE)
    quantity = models.IntegerField(verbose_name='liczebność grupy')
    group_number = models.IntegerField(verbose_name='numer grupy')


    class Meta:
        verbose_name = 'grupa'


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


class RoomItem(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)


class LecturerItem(models.Model):
    lecturer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)


DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)


class WeekDay(models.Model):
    lecturer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=DAYS_OF_WEEK)


class LecturerAvailability(models.Model):
    weekday = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
