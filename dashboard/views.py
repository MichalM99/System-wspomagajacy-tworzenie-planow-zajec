import datetime
import os

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse
from django.shortcuts import redirect, render

from account.models import Profile
from dashboard.forms import AddNewsForm
from dashboard.models import News
from dashboard.utils import generate_xlsx_personal
from schedule.forms import SearchRoom
from schedule.models import LecturerItem, RoomItem, Schedule, ScheduleItem, Room


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
        list.append(str(item.lecture) + ', ' + str(item.schedule.year.year_name)[:3] + '. ' + str(
            item.schedule.year.year_period) + str(item.schedule.year.type_of_semester)[:1] + ', ' + str(item.group)[
                                                                                                    :2] + '. ' + str(
            item.group.group_number))
        list.append(str(item.from_hour))
        list.append(str(item.to_hour))
        list.append(str(lecturer.lecturer))
        list.append(str(room.room))
        item = {item.get_weekday_display(): list}
        data_set.append(item)
    lecturer = Profile.objects.get(user=request.user)
    generate_xlsx_personal(lecturer, data_set, days)
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


def news_view(request):
    news = News.objects.all().order_by('-pub_date')
    paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)
    return render(request, 'dashboard/news_view.html', {
        'news': news,
    })


def delete_news(request, id):
    """Deletes single group based on pk."""
    query = News.objects.get(id=id)
    query.delete()
    return redirect(request.META['HTTP_REFERER'])


def add_news(request):
    if request.method == "POST":
        add_news_form = AddNewsForm(request.POST)
        if add_news_form.is_valid():
            cd = add_news_form.cleaned_data
            News.objects.create(
                author=Profile.objects.get(user=request.user),
                headline=cd['headline'],
                content=cd['content'],
                pub_date=datetime.datetime.now(),
            )
            return redirect(news_view)
    else:
        add_news_form = AddNewsForm()
    return render(request, "dashboard/add_news.html", {'add_news_form': add_news_form})


def pdf_view_personal(request, id):
    lecturer = Profile.objects.get(user=request.user)
    lecturer_name = str(lecturer).replace(' ', '_').replace('/', '_')
    filepath = os.path.join('schedules_pdf/{}_{}.pdf'.format(lecturer.id, lecturer_name))
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


def room_busy(request):
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

    days = []
    room_busy_dict = {}
    print(rooms)
    for room in rooms:
        room_items = RoomItem.objects.filter(room=room).order_by('schedule_item__from_hour')
        room_busy_dict[room] = {}
        for room_item in room_items:
            if room_item.schedule_item.get_weekday_display() not in days:
                days.append(room_item.schedule_item.get_weekday_display())
        for day in days:
            room_busy_dict[room][day] = []
        for room_item in room_items:
            room_busy_dict[room][room_item.schedule_item.get_weekday_display()].append(room_item)





    paginator = Paginator(rooms, 10)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)
    return render(request, "dashboard/room_busy.html", {
        'rooms': rooms, 'query': query, 'search_form': search_form, 'room_busy_dict': room_busy_dict, 'days': days,
    })

