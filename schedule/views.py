from django.shortcuts import render
from schedule.forms import AddAvailabilityForm
from schedule.models import WeekDay
from schedule.models import LecturerAvailability




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


def get_availability(request):
    """Returns availability list for current logged user/lecturer."""
    weekdays = WeekDay.objects.filter(lecturer=request.user)
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

