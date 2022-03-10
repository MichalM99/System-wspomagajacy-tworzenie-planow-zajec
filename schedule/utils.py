import datetime
import datetime as dt
import os

import xlsxwriter

from schedule.models import (Group, LecturerAvailability, LecturerItem, Room,
                             RoomItem, Schedule, ScheduleItem, WeekDay)


def generate_hours(step_minutes, start_hour, end_hour):
    """Function generates tuple with hours based on arguments."""
    hours = []
    for i in range(start_hour, end_hour):
        for j in range(int(60 / step_minutes)):
            time_str = str(i) + ':' + str(j * step_minutes).zfill(2)
            time = dt.datetime.strptime(time_str, '%H:%M')
            hours.append((time.time(), (str(i) + ':' + str(j * step_minutes).zfill(2))))
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
                availability_count += 1
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
    """Function check if room is free during specific time."""
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
    """Function checks if group can have classes at specific time."""
    schedule_items = ScheduleItem.objects.filter(group=group, weekday=weekday)
    for item in schedule_items:
        if not check_datetime(from_hour, to_hour, item):
            return False
    return True


def validate_availability(request, weekday, from_hour, to_hour):
    """Checks whether added availability doesn't interfere with already added."""
    weekdays = WeekDay.objects.filter(lecturer=request.user, weekday=weekday)
    if weekdays.count() > 0:
        for weekday in weekdays:
            availability = LecturerAvailability.objects.filter(weekday=weekday)
            for item in availability:
                if not check_availability(from_hour, to_hour, item):
                    return False
        return True
    else:
        return True


def get_availability(request):
    """Returns availability list for current logged user/lecturer."""
    weekdays = WeekDay.objects.filter(lecturer=request.user).order_by('weekday')
    availability_list = []
    for weekday in weekdays:
        availability_list.append(LecturerAvailability.objects.filter(weekday=weekday))
    return availability_list


def create_schedule_existance_list(results):
    """Returns list with True/False of schedule existance for every year."""
    existance_list = []
    for item in results:
        if Schedule.objects.filter(year=item):
            existance_list.append(True)
        else:
            existance_list.append(False)
    return existance_list


def get_schedule_ids(results):
    """Function returns schedule_ids for purpose of search bar."""
    schedule_ids = []
    for item in results:
        if Schedule.objects.filter(year=item):
            schedule_ids.append(Schedule.objects.get(year_id=item.id))
        else:
            schedule_ids.append(None)
    return schedule_ids


def check_group_existance(year_id, group_number):
    """Checks if specific year has groups assigned."""
    groups = Group.objects.filter(year_id=year_id, group_number=group_number)
    if groups:
        return True
    else:
        return False


def check_existing_room(room_name):
    """Returns whether room with specific name exists."""
    existing_rooms = Room.objects.filter(room_name=room_name)
    if existing_rooms:
        return True
    else:
        return False


def get_schedule_items_based_on_year_zip(year_id):
    """Function returns schedule_items for given year."""
    groups = Group.objects.filter(year_id=year_id).order_by('group_number')
    schedule_items_list = []
    lecturer_item_list = []

    for group in groups:
        for item in ScheduleItem.objects.filter(group=group).order_by('group__group_number'):
            schedule_items_list.append(item)
    for item in schedule_items_list:
        if LecturerItem.objects.filter(schedule_item=item).exists():
            lecturer_item_list.append(LecturerItem.objects.get(schedule_item=item))
        else:
            lecturer_item_list.append(None)
    return zip(schedule_items_list, lecturer_item_list)


def check_if_fits_lecturer_preferences(lecturer, from_hour, to_hour, weekday):
    """Checks whether specific time fits lecturer preferences."""
    weekdays = WeekDay.objects.filter(weekday=weekday, lecturer=lecturer)
    for weekday in weekdays:
        availabilities = LecturerAvailability.objects.filter(weekday=weekday)
        for availability in availabilities:
            availability_from_hour = datetime.datetime.strptime(str(availability.from_hour), '%H:%M:%S')
            availability_to_hour = datetime.datetime.strptime(str(availability.to_hour), '%H:%M:%S')
            if from_hour.time() >= availability_from_hour.time() and to_hour.time() <= availability_to_hour.time():
                return True
    return False


def check_if_lecturer_is_busy(lecturer, from_hour, to_hour, weekday):
    """Function check if lecturer is busy at specific time."""
    lecturer_items = LecturerItem.objects.filter(lecturer=lecturer)
    for item in lecturer_items:
        schedule_item = item.schedule_item
        if item.schedule_item.weekday == weekday:
            if not check_datetime(from_hour, to_hour, schedule_item):
                return False
    return True


def xslx_toPdf(year, row):
    """Function that converts xslx file to pdf."""
    year_name = str(year).replace(' ', '_').replace('/', '_')
    import asposecells
    import jpype
    if not jpype.isJVMStarted():
        jpype.startJVM()
    workbook = asposecells.api.Workbook("static/schedules_pdf/{}_{}.xlsx".format(year.id, year_name))
    saveOptions = asposecells.api.PdfSaveOptions()
    saveOptions.setOnePagePerSheet(True)
    workbook.save("static/schedules_pdf/{}_{}.pdf".format(year.id, year_name), saveOptions)


def generate_xlsx(year, data_dict, days_group):
    """Function that generates .xlsx file with schedule."""
    year_name = str(year).replace(' ', '_').replace('/', '_')
    if os.path.isfile('static/schedules_pdf/{}_{}.xlsx'.format(year.id, year_name)):
        return True
    workbook = xlsxwriter.Workbook('static/schedules_pdf/{}_{}.xlsx'.format(year.id, year_name))
    worksheet = workbook.add_worksheet()
    headings = [
        'Zajęcia',
        'Od:',
        'Do:',
        'Prowadzący',
        'Sala'
    ]
    # Zajęcia, Od, Do, Prowadzący, Sala

    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'white'})

    main_heading = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter', })

    worksheet.set_column(0, 0, 35)
    worksheet.set_column(1, 2, 8)
    worksheet.set_column(3, 3, 35)
    worksheet.set_column(4, 4, 8)

    day_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'color': 'white',
        'fg_color': 'black'})

    headings_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter', })

    classes_format = workbook.add_format({
        'bold': 1,
        'border': 1, })

    worksheet.merge_range('A{}:E{}'.format(1, 1), 'Plan: {}'.format(year_name), main_heading)
    row = 2
    for gr, d in days_group.items():
        worksheet.merge_range('A{}:E{}'.format(row, row), '{}'.format(gr), merge_format)
        row += 1
        for col in range(0, 5):
            worksheet.write(row - 1, col, headings[col], headings_format)
        for ds in d:
            row += 1
            worksheet.merge_range('A{}:E{}'.format(row, row), '{}'.format(ds), day_format)
            for item, val in data_dict.items():
                if item == gr:
                    for x in val:
                        for dy, z in x.items():
                            if ds == dy:
                                row += 1
                                for col in range(0, 5):
                                    worksheet.write(row - 1, col, z[col], classes_format)

        row += 3
    workbook.close()
    xslx_toPdf(year, row)


def get_days_of_week(schedule_items):
    """Function get all days that will appear in schedule."""
    days = []
    for item in schedule_items:
        if item.get_weekday_display() not in days:
            days.append(item.get_weekday_display())
    return days


def get_days_group(id):
    """Function returns dict with days of schedule_items for specific group."""
    schedule_items = ScheduleItem.objects.filter(schedule=Schedule.objects.get(id=id)).order_by('weekday', 'from_hour')
    data_dict = {}
    groups = []
    days_group = {}
    for schedule_item in schedule_items:
        data_dict[schedule_item.group] = []
        if schedule_item.group not in groups:
            groups.append(schedule_item.group)

    mapping = {
        "Poniedziałek": 1,
        "Wtorek": 2,
        "Środa": 3,
        "Czwartek": 4,
        "Piątek": 5,
        "Sobota": 6,
        "Niedziela": 7
    }

    for group in groups:
        days_group[group] = []
        items = ScheduleItem.objects.filter(group=group)
        for item in items:
            if item.get_weekday_display() not in days_group[group]:
                days_group[group].append(item.get_weekday_display())
        days_group[group] = sorted(days_group[group], key=lambda x: mapping[x])
    return days_group


def get_schedule_items_for_year(year_id):
    """Function that return every schedule_item assigned to specific year."""
    groups = Group.objects.filter(year_id=year_id)
    schedule_items = []
    for group in groups:
        for item in ScheduleItem.objects.filter(group=group):
            schedule_items.append(item)
    return schedule_items


def is_there_unassigned_item(year_id):
    """Function that checks whether any unassigned schedule_item exists."""
    schedule_items = get_schedule_items_for_year(year_id)
    for item in schedule_items:
        if item.schedule is None:
            return True
    return False
