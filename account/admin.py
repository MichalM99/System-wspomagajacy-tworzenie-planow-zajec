from django.contrib import admin

import schedule.models
import account.models

# Register your models here.

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
admin.site.register(account.models.Profile)