import datetime

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.views.generic import View

from account.models import Profile
from dashboard.views import get_schedule_items_for_lecturer
from schedule.forms import (AddAvailabilityForm, AddGroupForm, AddRoomForm,
                            AddRoomToScheduleForm, AddScheduleForm,
                            AddScheduleItemForm, AddYear, EditRoomForm,
                            ManageYearForm, SearchRoom, SearchYear)
from schedule.models import (Group, LecturerAvailability, LecturerItem, Room,
                             RoomItem, Schedule, ScheduleItem, WeekDay, Year)
from schedule.utils import (check_availability, check_datetime, is_group_free,
                            is_lecturer_free, is_room_free)


def set_preferences(request):
    """Allows to add preferences for lecturer."""
    availability = get_availability(request)
    if request.method == 'POST':
        form = AddAvailabilityForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            current_user = request.user
            if validate_availability(request, cd['weekday'], cd['from_hour'], cd['to_hour']) != True or \
                    cd['from_hour'] >= cd['to_hour']:
                error = "Podaj właściwe czasy, podane godziny zachodzą na siebie, bądź są nieprawidłowe!"
                return render(request, 'schedule/set_preferences.html',
                              {'form': form, 'availability': availability, 'error': error})
            else:
                weekday = WeekDay.objects.create(lecturer=current_user, weekday=cd['weekday'])
                LecturerAvailability.objects.create(weekday=weekday, from_hour=cd['from_hour'], to_hour=cd['to_hour'])
                availability = get_availability(request)
                return render(request, 'schedule/set_preferences.html',
                              {'form': form, 'availability': availability})
    else:
        form = AddAvailabilityForm()
    return render(request, 'schedule/set_preferences.html',
                  {'form': form, 'availability': availability})


def delete_availability(request, id):
    """Deletes single availability based on pk."""
    query = WeekDay.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def get_availability(request):
    """Returns availability list for current logged user/lecturer."""
    weekdays = WeekDay.objects.filter(lecturer=request.user).order_by('weekday')
    availability_list = []
    for weekday in weekdays:
        availability_list.append(LecturerAvailability.objects.filter(weekday=weekday))
    return availability_list


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


def create_schedule_existance_list(results):
    existance_list = []
    for item in results:
        if Schedule.objects.filter(year=item):
            existance_list.append(True)
        else:
            existance_list.append(False)
    return existance_list


def get_schedule_ids(results):
    schedule_ids = []
    for item in results:
        if Schedule.objects.filter(year=item):
            schedule_ids.append(Schedule.objects.get(year_id=item.id))
        else:
            schedule_ids.append(None)
    return schedule_ids


def year_group_management(request):
    form = SearchYear()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchYear(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Year.objects.filter(
                Q(year_name__icontains=query) | Q(year_period__icontains=query) | Q(speciality__icontains=query)
            )
            if query == '':
                results = Year.objects.all()
    else:
        results = Year.objects.all()
    schedule_ids = get_schedule_ids(results)
    results = list(zip(results, create_schedule_existance_list(results), schedule_ids))
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'schedule/year_group_management.html', {'form': form,
                                                                   'query': query,
                                                                   'page_obj': page_obj})


def add_year(request):
    if request.method == 'POST':
        year_form = AddYear(request.POST)
        if year_form.is_valid():
            cd = year_form.cleaned_data
            Year.objects.create(year_name=cd['year_name'], speciality=cd['speciality'], year_period=cd['year_period'],
                                type_of_studies=cd['type_of_studies'], type_of_semester=cd['type_of_semester'])
            return redirect(year_group_management)
    else:
        year_form = AddYear()
    return render(request, 'schedule/add_year.html', {'year_form': year_form})


def manage_year(request, id):
    """Basically DetailView for Year model."""
    groups = Group.objects.filter(year_id=id).order_by('group_number')
    data = get_object_or_404(Year, pk=id)
    if request.method == "POST":
        form = ManageYearForm(instance=data, data=request.POST)
        if form.is_valid():
            form.save()
        return redirect(year_group_management)
    else:
        form = ManageYearForm(instance=data)
    return render(request, 'schedule/manage_year.html', {
        "data": data, "form": form, "groups": groups
    })


def check_group_existance(year_id, group_number):
    groups = Group.objects.filter(year_id=year_id, group_number=group_number)
    if groups:
        return True
    else:
        return False


def add_group(request, id):
    if request.method == "POST":
        form = AddGroupForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if check_group_existance(id, cd['group_number']):
                error = "Grupa o podanym numerze już istnieje!"
                return render(request, 'schedule/add_group.html',
                              {'form': form, 'error': error, 'id': id})
            Group.objects.create(year_id=id, quantity=cd['quantity'], group_number=cd['group_number'])
            return redirect("/schedule/manage_year/{id}/".format(id=id))
    else:
        form = AddGroupForm()
    return render(request, 'schedule/add_group.html', {'form': form, 'id': id})


def delete_group(request, id, pk):
    """Deletes single group based on pk."""
    query = Group.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def delete_year(request, id):
    """Deletes single group based on pk."""
    query = Year.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def check_existing_room(room_name):
    existing_rooms = Room.objects.filter(room_name=room_name)
    if existing_rooms:
        return True
    else:
        return False


def manage_room(request):
    search_form = SearchRoom()
    query = None
    rooms = []
    if 'query' in request.GET:
        search_form = SearchRoom(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            rooms = Room.objects.filter(room_name=query)
            if query == '':
                rooms = Room.objects.all()
    else:
        rooms = Room.objects.all()
    if request.method == "POST":
        form = AddRoomForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if check_existing_room(cd['room_name']):
                error = "Taka sala juz istnieje!"
                return render(request, 'schedule/manage_room.html',
                              {'form': form, 'rooms': rooms, 'error': error, 'query': query,
                               'search_form': search_form})
            new_room = form.save(commit=False)
            new_room.save()
    else:
        form = AddRoomForm()
    paginator = Paginator(rooms, 10)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)
    return render(request, 'schedule/manage_room.html', {
        'form': form, 'rooms': rooms, 'query': query, 'search_form': search_form
    })


def delete_room(request, id):
    """Deletes single group based on pk."""
    query = Room.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def edit_room(request, id):
    """Functional DetailView for Room model."""
    data = get_object_or_404(Room, pk=id)
    room_name = data.room_name
    if request.method == "POST":
        form = EditRoomForm(instance=data, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data['room_name']
            if room_name == cd:
                print("haha")
            elif check_existing_room(cd):
                error = "Taka sala juz istnieje!"
                return render(request, 'schedule/edit_room.html',
                              {'form': form, 'error': error})
            form.save()
        return redirect("/schedule/manage_room/")
    else:
        form = EditRoomForm(instance=data)
    return render(request, 'schedule/edit_room.html', {'form': form, 'data': data})


def manage_schedule(request):
    """Basic view for schedules."""
    schedules = Schedule.objects.all()
    paginator = Paginator(schedules, 10)
    page_number = request.GET.get('page')
    schedules = paginator.get_page(page_number)
    # print(is_lecturer_free(User.objects.get(id=request.user.id), 0, datetime.datetime.strptime('13:15', '%H:%M').time(), datetime.datetime.strptime('14:30', '%H:%M').time()))
    # print(is_room_free(Room.objects.get(room_name='15'), datetime.datetime.strptime('12:50', '%H:%M').time(), datetime.datetime.strptime('13:30', '%H:%M').time(), 0))
    # print(is_group_free(Group.objects.get(id=12), datetime.datetime.strptime('13:15', '%H:%M').time(), datetime.datetime.strptime('13:45', '%H:%M').time(), 0))
    return render(request, 'schedule/manage_schedule.html', {'schedules': schedules})


def delete_schedule(request, pk):
    """Deletes single schedule based on pk."""
    query = Schedule.objects.get(year_id=pk)
    print(query)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def delete_schedule_item(request, id):
    """Deletes single schedule item based on pk."""
    query = ScheduleItem.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def edit_schedule(request, id):
    """Edit schedule view."""
    return render(request, 'schedule/edit_schedule.html', {})


def get_schedule_items_based_on_year_zip(year_id):
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


def create_schedule(request, id):
    """Create schedule view."""
    schedule_items = get_schedule_items_based_on_year_zip(id)
    add_schedule_item_form = AddScheduleItemForm(year_id=id)
    add_schedule_form = AddScheduleForm()
    if request.method == 'POST':
        if 'add_schedule_item' in request.POST:
            add_schedule_item_form = AddScheduleItemForm(request.POST, year_id=id)
            if add_schedule_item_form.is_valid():
                cd = add_schedule_item_form.cleaned_data
                schedule_item = ScheduleItem.objects.create(group=cd['group'], lecture=cd['lecture'],
                                                            lecture_units=cd['lecture_unit'])
                LecturerItem.objects.create(schedule_item=schedule_item, lecturer=cd['lecturer'])
                add_schedule_item_form = AddScheduleItemForm(year_id=id)
                schedule_items = get_schedule_items_based_on_year_zip(id)
                return render(request, 'schedule/create_schedule.html', {
                    'add_schedule_form': add_schedule_form,
                    'add_schedule_item_form': add_schedule_item_form,
                    'schedule_items': schedule_items,
                })
        elif 'create_schedule' in request.POST:
            add_schedule_form = AddScheduleForm(request.POST)
            if add_schedule_form.is_valid():
                cd = add_schedule_form.cleaned_data
                items_count = len(list(schedule_items)) < 1
                if items_count:
                    return render(request, 'schedule/create_schedule.html', {
                        'add_schedule_form': add_schedule_form,
                        'add_schedule_item_form': add_schedule_item_form,
                        'schedule_items': schedule_items,
                        'items_count': items_count,
                    })
                is_generated = generate_schedule(id, cd)
                if is_generated == False:
                    return render(request, 'schedule/create_schedule.html', {
                        'add_schedule_form': add_schedule_form,
                        'add_schedule_item_form': add_schedule_item_form,
                        'schedule_items': schedule_items,
                        'is_generated': is_generated,
                    })
                return redirect(year_group_management)
    else:
        add_schedule_form = AddScheduleForm()
        add_schedule_item_form = AddScheduleItemForm(year_id=id)

    return render(request, 'schedule/create_schedule.html', {
        'add_schedule_form': add_schedule_form,
        'add_schedule_item_form': add_schedule_item_form,
        'schedule_items': schedule_items,
    })


def check_if_fits_lecturer_preferences(lecturer, from_hour, to_hour, weekday):
    """Checks whether lecturer can be assigned to classes."""
    weekdays = WeekDay.objects.filter(weekday=weekday, lecturer=lecturer)
    availability_count = 0
    for weekday in weekdays:
        availabilities = LecturerAvailability.objects.filter(weekday=weekday)
        for availability in availabilities:
            availability_from_hour = datetime.datetime.strptime(str(availability.from_hour), '%H:%M:%S')
            availability_to_hour = datetime.datetime.strptime(str(availability.to_hour), '%H:%M:%S')
            if from_hour.time() >= availability_from_hour.time() and to_hour.time() <= availability_to_hour.time():
                return True
    return False


def check_if_lecturer_is_busy(lecturer, from_hour, to_hour, weekday):
    lecturer_items = LecturerItem.objects.filter(lecturer=lecturer)
    for item in lecturer_items:
        schedule_item = item.schedule_item
        if item.schedule_item.weekday == weekday:
            if not check_datetime(from_hour, to_hour, schedule_item):
                return False
    return True


def is_room_free(schedule_item, from_hour, to_hour, weekday):
    rooms = Room.objects.filter(type_of_lecture=schedule_item.lecture.type_of_lecture)
    for room in rooms:
        room_items = RoomItem.objects.filter(room=room)
        for item in room_items:
            schedule_item = item.schedule_item
            if item.schedule_item.weekday == weekday:
                if not check_datetime(from_hour, to_hour, schedule_item):
                    return False
        return room
    return False


def generate_schedule(year_id, schedule_data):
    """Function that generates schedule based on added schedule items."""
    break_time = datetime.timedelta(minutes=schedule_data['break_time'] - 15)  # Minimalna przerwa
    lecture_unit_duration = schedule_data['lecture_unit']  # Czas trwania pojedynczej jednostki lekcyjnej
    schedule_items = get_schedule_items_based_on_year_zip(year_id)
    delta = datetime.timedelta(minutes=15)
    start_time = datetime.datetime(1900, 1, 1, 8, 0, 0)
    end_time = datetime.datetime(1900, 1, 1, 21, 0, 0)
    schedule = Schedule.objects.create(year_id=year_id, lecture_unit=lecture_unit_duration,
                                       break_time=schedule_data['break_time'] - 15)
    year = Year.objects.get(id=year_id)
    if year.type_of_studies == 'stacjonarne':
        start_day = 0
        end_day = 4
    elif year.type_of_studies == 'niestacjonarne':
        start_day = 4
        end_day = 6

    for schedule_item, lecturer in schedule_items:
        skip_loop = True
        day_of_week = start_day
        while day_of_week <= end_day and skip_loop:
            duration_time = datetime.timedelta(minutes=schedule_item.lecture_units * lecture_unit_duration)
            while start_time + duration_time < end_time:
                group_free = is_group_free(schedule_item.group, start_time - break_time,
                                           start_time + duration_time + break_time, day_of_week)
                lecturer_free = check_if_fits_lecturer_preferences(lecturer.lecturer.user, start_time - break_time,
                                                                   start_time + duration_time + break_time,
                                                                   day_of_week)
                lecturer_busy = check_if_lecturer_is_busy(lecturer.lecturer, start_time - break_time,
                                                          start_time + duration_time + break_time,
                                                          day_of_week)
                room_free = is_room_free(schedule_item, start_time, start_time + duration_time, day_of_week)
                can_assign_time = group_free and lecturer_free and lecturer_busy and room_free != False
                # print(str(group_free) + str(lecturer_free) + str(lecturer_busy) + str(room_free != False))
                if can_assign_time:
                    ScheduleItem.objects.filter(id=schedule_item.id).update(schedule=schedule,
                                                                            from_hour=start_time.time(),
                                                                            to_hour=(start_time + duration_time).time(),
                                                                            weekday=day_of_week)
                    RoomItem.objects.create(room=room_free, schedule_item_id=schedule_item.id)
                    day_of_week = 0
                    skip_loop = False
                    start_time = datetime.datetime(1900, 1, 1, 8, 0, 0)
                    break
                start_time += delta
            day_of_week += 1
            start_time = datetime.datetime(1900, 1, 1, 8, 0, 0)

    if is_there_unassigned_item(year_id):
        print('nie mozna utworzyć planu')
        Schedule.objects.filter(id=schedule.id).delete()
        return False  # Returns False if plan couldn't be generated
    return True  # Returns True if plan could be generated

    # przypisać generowanie tylko na poszczególne dni
    # from_hour = dt.datetime.strptime(str(from_hour), '%H:%M:%S')
    # to_hour = dt.datetime.strptime(str(to_hour), '%H:%M:%S')
    # from_hour = (from_hour - dt.timedelta(minutes=15)).time()
    # to_hour = (to_hour + dt.timedelta(minutes=15)).time()


def get_schedule_items_for_year(year_id):
    groups = Group.objects.filter(year_id=year_id)
    schedule_items = []
    for group in groups:
        for item in ScheduleItem.objects.filter(group=group):
            schedule_items.append(item)
    return schedule_items


def is_there_unassigned_item(year_id):
    schedule_items = get_schedule_items_for_year(year_id)
    for item in schedule_items:
        if item.schedule is None:
            return True
    return False


def schedule_view(request, id):
    schedule_items = ScheduleItem.objects.filter(schedule=Schedule.objects.get(id=id)).order_by('weekday', 'from_hour')
    year = Schedule.objects.get(id=id).year
    data_set = []
    data_dict = {}
    groups = []
    days_group = {}
    for schedule_item in schedule_items:
        data_dict[schedule_item.group] = []
        if schedule_item.group not in groups:
            groups.append(schedule_item.group)

    for group in groups:
        days_group[group] = []
        items = ScheduleItem.objects.filter(group=group)
        for item in items:
            if item.get_weekday_display() not in days_group[group]:
                days_group[group].append(item.get_weekday_display())
        days_group[group].sort()

    for schedule_item in schedule_items:
        lecturer = LecturerItem.objects.get(schedule_item=schedule_item)
        room = RoomItem.objects.get(schedule_item=schedule_item)
        list = []
        list.append(str(schedule_item.lecture))
        list.append(str(schedule_item.from_hour))
        list.append(str(schedule_item.to_hour))
        list.append(str(lecturer.lecturer))
        list.append(str(room.room))
        item = {schedule_item.get_weekday_display(): list}
        data_set.append(item)
        data_dict[schedule_item.group].append(item)
    return render(request, 'schedule/schedule_view.html', {
        'data_set': data_set,
        'data_dict': data_dict,
        'days_group': days_group,
        'year': year,
    })


def get_days_of_week(schedule_items):
    days = []
    for item in schedule_items:
        if item.get_weekday_display() not in days:
            days.append(item.get_weekday_display())
    return days









