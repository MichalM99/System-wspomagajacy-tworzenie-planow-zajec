import datetime
import os

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from schedule.forms import (AddAvailabilityForm, AddGroupForm, AddLectureForm,
                            AddRoomForm, AddScheduleForm, AddScheduleItemForm,
                            AddYear, EditRoomForm, ManageYearForm, SearchRoom,
                            SearchYear)
from schedule.models import (Group, Lecture, LecturerAvailability,
                             LecturerItem, Room, RoomItem, Schedule,
                             ScheduleItem, WeekDay, Year)
from schedule.utils import (check_datetime,
                            check_existing_room, check_group_existance,
                            check_if_fits_lecturer_preferences,
                            check_if_lecturer_is_busy,
                            create_schedule_existance_list, generate_xlsx,
                            get_availability, get_schedule_ids,
                            get_schedule_items_based_on_year_zip,
                            is_group_free, is_room_free,
                            is_there_unassigned_item, validate_availability)


@login_required
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


@login_required
def delete_availability(request, id):
    """Deletes single availability based on pk."""
    query = WeekDay.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def year_group_management(request):
    """View responsible for managins year's groups."""
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


@login_required
def add_year(request):
    """View responsible for adding year."""
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


@login_required
def manage_year(request, id):
    """Basically DetailView for Year model."""
    groups = Group.objects.filter(year_id=id).order_by('group_number')
    lectures = Lecture.objects.filter(year_id=id).order_by('lecture_name')
    data = get_object_or_404(Year, pk=id)
    if request.method == "POST":
        if 'save_changes' in request.POST:
            form = ManageYearForm(instance=data, data=request.POST)
            if form.is_valid():
                form.save()
            return redirect(year_group_management)
        elif 'add_lecture' in request.POST:
            form = ManageYearForm(instance=data)
            add_lecture_form = AddLectureForm(request.POST)
            print(add_lecture_form.is_valid())
            if add_lecture_form.is_valid():
                print("abc")
                cd = add_lecture_form.cleaned_data
                Lecture.objects.create(year_id=id, lecture_name=cd['lecture_name'],
                                       type_of_lecture=cd['type_of_lecture'])
                lectures = Lecture.objects.filter(year_id=id).order_by('lecture_name')
            return render(request, 'schedule/manage_year.html', {
                "data": data, "form": form, "groups": groups, 'id': id,
                "lectures": lectures, 'add_lecture_form': add_lecture_form,
            })
    else:
        form = ManageYearForm(instance=data)
        add_lecture_form = AddLectureForm()
    return render(request, 'schedule/manage_year.html', {
        "data": data, "form": form, "groups": groups, 'id': id,
        "lectures": lectures, 'add_lecture_form': add_lecture_form,
    })


@login_required
def add_group(request, id):
    """View responsible for adding groups to specific year."""
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


@login_required
def delete_group(request, id, pk):
    """Deletes single group based on pk."""
    query = Group.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def delete_year(request, id):
    """Deletes single group based on pk."""
    query = Year.objects.get(id=id)
    query.delete()
    return redirect(year_group_management)


@login_required
def manage_room(request):
    """View for managing rooms."""
    search_form = SearchRoom()
    query = None
    rooms = []
    if 'query' in request.GET:
        search_form = SearchRoom(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            rooms = Room.objects.filter(room_name__contains=query)
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


@login_required
def delete_room(request, id):
    """Deletes single group based on pk."""
    query = Room.objects.get(id=id)
    query.delete()
    return redirect(manage_room)


@login_required
def edit_room(request, id):
    """Functional DetailView for Room model."""
    data = get_object_or_404(Room, pk=id)
    room_name = data.room_name
    if request.method == "POST":
        form = EditRoomForm(instance=data, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data['room_name']
            if room_name == cd:
                print("x")
            elif check_existing_room(cd):
                error = "Taka sala juz istnieje!"
                return render(request, 'schedule/edit_room.html',
                              {'form': form, 'error': error})
            form.save()
        return redirect("/schedule/manage_room/")
    else:
        form = EditRoomForm(instance=data)
    return render(request, 'schedule/edit_room.html', {'form': form, 'data': data, 'id': id})


@login_required
def delete_schedule(request, pk):
    """Deletes single schedule based on pk."""
    query = Schedule.objects.get(year_id=pk)
    query.delete()
    return redirect(year_group_management)


@login_required
def delete_schedule_item(request, id):
    """Deletes single schedule item based on pk."""
    query = ScheduleItem.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required
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


def is_room_free(schedule_item, from_hour, to_hour, weekday):
    """Function that checks whether room is free during specific time."""
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
    break_time = datetime.timedelta(minutes=schedule_data['break_time'] - 15)
    lecture_unit_duration = schedule_data['lecture_unit']
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
                if can_assign_time:
                    ScheduleItem.objects.filter(id=schedule_item.id).update(schedule=schedule,
                                                                            from_hour=start_time.time(),
                                                                            to_hour=(start_time + duration_time).time(),
                                                                            weekday=day_of_week)
                    RoomItem.objects.create(room=room_free, schedule_item_id=schedule_item.id)
                    day_of_week = 0
                    skip_loop = False
                    break
                start_time += delta
            day_of_week += 1
            start_time = datetime.datetime(1900, 1, 1, 8, 0, 0)

    if is_there_unassigned_item(year_id):
        Schedule.objects.filter(id=schedule.id).delete()
        return False  # Returns False if plan couldn't be generated
    return True  # Returns True if plan could be generated


@login_required
def schedule_view(request, id):
    """View of specific schedule."""
    schedule_items = ScheduleItem.objects.filter(schedule=Schedule.objects.get(id=id)).order_by('weekday', 'from_hour')
    year = Schedule.objects.get(id=id).year
    schedule_id = Schedule.objects.get(id=id).id
    data_set = []
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
    generate_xlsx(year, data_dict, days_group)
    return render(request, 'schedule/schedule_view.html', {
        'data_set': data_set,
        'data_dict': data_dict,
        'days_group': days_group,
        'year': year,
        'schedule_id': schedule_id,
    })


def pdf_view(request, id):
    """Function opens PDF file with schedule table."""
    year = Year.objects.get(id=id)
    year_name = str(year).replace(' ', '_').replace('/', '_')
    filepath = os.path.join('static/schedules_pdf/{}_{}.pdf'.format(year.id, year_name))
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


@login_required
def delete_lecture(request, id, pk):
    """Function deletes single group based on pk."""
    query = Lecture.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def external_schedule_view(request, id):
    """View for exporting schedule to the outsiders."""
    schedule_items = ScheduleItem.objects.filter(
        schedule=Schedule.objects.get(id=id)).order_by('weekday', 'from_hour')
    year = Schedule.objects.get(id=id).year
    data_set = []
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
    return render(request, 'schedule/external_schedule_view.html', {
        'data_set': data_set,
        'data_dict': data_dict,
        'days_group': days_group,
        'year': year,
    })
