from django.contrib import admin

import schedule.models
from account.models import Profile


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'academic_degree']


admin.site.register(schedule.models.Schedule)
admin.site.register(schedule.models.Year)
admin.site.register(schedule.models.Group)
admin.site.register(schedule.models.Lecture)
admin.site.register(schedule.models.ScheduleItem)
admin.site.register(schedule.models.Room)
admin.site.register(schedule.models.RoomItem)
admin.site.register(schedule.models.LecturerItem)
admin.site.register(schedule.models.WeekDay)
admin.site.register(schedule.models.LecturerAvailability)
