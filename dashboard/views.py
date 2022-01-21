from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from account.models import Profile
from schedule.models import Schedule, ScheduleItem, LecturerItem, RoomItem


@login_required
def dashboard_view(request):
    schedule_items = get_schedule_items_for_lecturer(request.user)
    days = []
    data_set = []
    for item in schedule_items:
        list = []
        lecturer = LecturerItem.objects.get(schedule_item=item)
        room = RoomItem.objects.get(schedule_item=item)
        if item.get_weekday_display() not in days:
            days.append(item.get_weekday_display())
        list.append(str(item.lecture))
        list.append(str(item.from_hour))
        list.append(str(item.to_hour))
        list.append(str(lecturer.lecturer))
        list.append(str(room.room))
        item = {item.get_weekday_display(): list}
        data_set.append(item)
    lecturer = Profile.objects.get(user=request.user)
    return render(request, 'dashboard/dashboard.html', {
        'schedule_items': schedule_items,
        'days': days,
        'data_set': data_set,
        'lecturer': lecturer,
    })


def get_schedule_items_for_lecturer(lecturer):
    lecturer_items = LecturerItem.objects.filter(lecturer=Profile.objects.get(user=lecturer)).order_by(
        'schedule_item__weekday', 'schedule_item__from_hour')
    schedule_items = []
    for item in lecturer_items:
        schedule_items.append(item.schedule_item)
    return schedule_items


# def schedule_view(request, id):
#     schedule_items = ScheduleItem.objects.filter().order_by('weekday', 'from_hour')
#     data_set = []
#     data_dict = {}
#     groups = []
#     days_group = {}
#     for schedule_item in schedule_items:
#         data_dict[schedule_item.group] = []
#         if schedule_item.group not in groups:
#             groups.append(schedule_item.group)
#
#     for group in groups:
#         days_group[group] = []
#         items = ScheduleItem.objects.filter(group=group)
#         for item in items:
#             if item.get_weekday_display() not in days_group[group]:
#                 days_group[group].append(item.get_weekday_display())
#         days_group[group].sort()
#
#     for schedule_item in schedule_items:
#         lecturer = LecturerItem.objects.get(schedule_item=schedule_item)
#         room = RoomItem.objects.get(schedule_item=schedule_item)
#         list = []
#         list.append(str(schedule_item.lecture))
#         list.append(str(schedule_item.from_hour))
#         list.append(str(schedule_item.to_hour))
#         list.append(str(lecturer.lecturer))
#         list.append(str(room.room))
#         item = {schedule_item.get_weekday_display(): list}
#         data_set.append(item)
#         data_dict[schedule_item.group].append(item)
#     return render(request, 'schedule/schedule_view.html', {
#         'data_set': data_set,
#         'data_dict': data_dict,
#         'days_group': days_group,
#     })
