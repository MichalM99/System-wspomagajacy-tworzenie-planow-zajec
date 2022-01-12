import datetime as dt




def generate_hours(step_minutes, start_hour, end_hour):
    hours = []
    for i in range(start_hour, end_hour):
        for j in range(int(60/step_minutes)):
            time_str = str(i) + ':' + str(j*step_minutes).zfill(2)
            time = dt.datetime.strptime(time_str, '%H:%M')
            hours.append((time.time(), (str(i) + ':' + str(j*step_minutes).zfill(2))))
    return tuple(hours)