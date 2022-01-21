import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from account.models import Profile
from dashboard.forms import AddNewsForm
from dashboard.models import News
from schedule.models import LecturerItem, RoomItem, Schedule, ScheduleItem


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

