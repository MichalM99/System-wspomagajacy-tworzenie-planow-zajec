from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from schedule.models import Schedule, ScheduleItem, LecturerItem, RoomItem



@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html', {})



