from django.shortcuts import render
from schedule.forms import AddAvailabilityForm, AddYear, AddGroup, SearchYear
from schedule.models import WeekDay
from schedule.models import LecturerAvailability
from schedule.models import Year, Group
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator




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
                if from_hour <= item.to_hour and from_hour >= item.from_hour:
                    print("Pierwszy if")
                    return False
                if to_hour >= item.to_hour and from_hour <= item.from_hour:
                    print("Drugi if")
                    return False
                if to_hour == item.to_hour and from_hour == item.from_hour:
                    print("Trzeci if")
                    return False
                if from_hour <= item.from_hour and to_hour >= item.from_hour:
                    print("Czwarty if")
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
    return render(request, 'schedule/add_year.html',{'year_form': year_form})


def add_group(request):
    return render(request, 'schedule/add_group.html',{})