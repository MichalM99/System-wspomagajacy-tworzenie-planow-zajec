import datetime
import datetime as dt
import json

from schedule.models import Room, Profile, LecturerAvailability, WeekDay, ScheduleItem, LecturerItem, RoomItem


def generate_hours(step_minutes, start_hour, end_hour):
    hours = []
    for i in range(start_hour, end_hour):
        for j in range(int(60/step_minutes)):
            time_str = str(i) + ':' + str(j*step_minutes).zfill(2)
            time = dt.datetime.strptime(time_str, '%H:%M')
            hours.append((time.time(), (str(i) + ':' + str(j*step_minutes).zfill(2))))
    return tuple(hours)


def check_availability(from_hour, to_hour, item):
    """Checks whether lecturer availability is already added or conflicted."""
    if from_hour > to_hour:
        return False
    if from_hour <= item.to_hour and from_hour >= item.from_hour:
        return False
    if to_hour >= item.to_hour and from_hour <= item.from_hour:
        return False
    if to_hour == item.to_hour and from_hour == item.from_hour:
        return False
    if from_hour <= item.from_hour and to_hour >= item.from_hour:
        return False
    return True




def is_lecturer_free(lecturer, weekday, from_hour, to_hour):
    """Checks whether lecturer can be assigned to classes."""
    weekdays = WeekDay.objects.filter(weekday=weekday, lecturer=lecturer)
    availability_count = 0
    # from_hour = dt.datetime.strptime(str(from_hour), '%H:%M:%S')
    # to_hour = dt.datetime.strptime(str(to_hour), '%H:%M:%S')
    for weekday in weekdays:
        availability = LecturerAvailability.objects.filter(weekday=weekday)
        for item in availability:
            if from_hour >= item.from_hour and to_hour <= item.to_hour:
                availability_count+=1
    if availability_count < 1:
        return False


    from_hour = (from_hour - dt.timedelta(minutes=15)).time()
    to_hour = (to_hour + dt.timedelta(minutes=15)).time()

    lecturer_items = LecturerItem.objects.filter(lecturer=lecturer)
    for item in lecturer_items:
        schedule_item = item.schedule_item
        if schedule_item.weekday == weekday.weekday:
            if not check_availability(from_hour, to_hour, schedule_item):
                return False
    return True


def is_room_free(room, from_hour, to_hour, weekday):
    room_items = RoomItem.objects.filter(room=room)
    for item in room_items:
        schedule_item = item.schedule_item
        if schedule_item.weekday == weekday:
            if not check_availability(from_hour, to_hour, schedule_item):
                return False
    return True

def check_datetime(from_hour, to_hour, item):
    """Checks whether lecturer availability is already added or conflicted."""
    item_from_hour = datetime.datetime.strptime(str(item.from_hour), '%H:%M:%S')
    item_to_hour = datetime.datetime.strptime(str(item.to_hour), '%H:%M:%S')
    if from_hour > to_hour:
        return False
    if from_hour <= item_to_hour and from_hour >= item_from_hour:
        return False
    if to_hour >= item_to_hour and from_hour <= item_from_hour:
        return False
    if to_hour == item_to_hour and from_hour == item_from_hour:
        return False
    if from_hour <= item_from_hour and to_hour >= item_from_hour:
        return False
    return True



def is_group_free(group, from_hour, to_hour, weekday):
    schedule_items = ScheduleItem.objects.filter(group=group, weekday=weekday)
    for item in schedule_items:
        if not check_datetime(from_hour, to_hour, item):
            return False
    return True



