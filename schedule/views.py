from django.contrib.auth.models import User
from django.shortcuts import render
from schedule.forms import AddAvailabilityForm, AddYear, AddGroupForm, SearchYear, ManageYearForm, AddRoomForm, \
    SearchRoom, EditRoomForm, AddScheduleForm, AddScheduleItemForm
from schedule.models import WeekDay
from schedule.models import LecturerAvailability
from schedule.models import Year, Group, Room, Schedule
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator
from schedule.utils import check_availability, is_lecturer_free, is_room_free, is_group_free
from account.models import Profile
import datetime
import json

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
    groups = Group.objects.filter(year_id=id)
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
    #print(is_lecturer_free(User.objects.get(id=request.user.id), 0, datetime.datetime.strptime('13:15', '%H:%M').time(), datetime.datetime.strptime('14:30', '%H:%M').time()))
    #print(is_room_free(Room.objects.get(room_name='15'), datetime.datetime.strptime('12:50', '%H:%M').time(), datetime.datetime.strptime('13:30', '%H:%M').time(), 0))
    #print(is_group_free(Group.objects.get(id=12), datetime.datetime.strptime('13:15', '%H:%M').time(), datetime.datetime.strptime('13:45', '%H:%M').time(), 0))
    return render(request, 'schedule/manage_schedule.html', {'schedules': schedules})


def delete_schedule(request, id):
    """Deletes single schedule based on pk."""
    query = Schedule.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def edit_schedule(request, id):
    """Edit schedule view."""
    return render(request, 'schedule/edit_schedule.html', {})



def create_schedule(request):
    """Create schedule view."""
    #is_lecturer_free() - done
    #is_room_free() - done
    #is_group_free() - done
    add_schedule_form = AddScheduleForm()
    add_schedule_item_form = AddScheduleItemForm()
    items = Year.objects.all()
    if request.method == "POST":
        form = AddScheduleForm(request.POST)
        print("abc")
        if form.is_valid():
            print(form)
            cd = form.cleaned_data
            # Schedule.objects.create(schedule_name=cd['schedule_name'], lecture_unit=cd['lecture_unit'],
            #                         break_time=cd['break_time'], year=cd['year'])
            print(cd)
    #Schedule.objects.create()
    return render(request, 'schedule/create_schedule.html', {
        'add_schedule_form': add_schedule_form,
        'add_schedule_item_form': add_schedule_item_form,
        'items': items})


