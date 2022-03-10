import os

import xlsxwriter

from account.models import Profile
from schedule.models import LecturerItem
from schedule.utils import xslx_toPdf


def generate_xlsx_personal(lecturer, data_dict, days):
    """Function that generates pdf file with lecturers personal plan."""
    year_name = str(lecturer).replace(' ', '_').replace('/', '_')
    if os.path.isfile('static/schedules_pdf/{}_{}.xlsx'.format(lecturer.id, year_name)):
        return True
    workbook = xlsxwriter.Workbook('static/schedules_pdf/{}_{}.xlsx'.format(lecturer.id, year_name))
    worksheet = workbook.add_worksheet()
    headings = [
        'Zajęcia',
        'Od:',
        'Do:',
        'Prowadzący',
        'Sala'
    ]

    main_heading = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter', })

    worksheet.set_column(0, 0, 46)
    worksheet.set_column(1, 2, 8)
    worksheet.set_column(3, 3, 25)
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
    for col in range(0, 5):
        worksheet.write(row - 1, col, headings[col], headings_format)
    for d in days:
        row += 1
        worksheet.merge_range('A{}:E{}'.format(row, row), '{}'.format(d), day_format)
        for val in data_dict:
            for dy, z in val.items():
                if d == dy:
                    row += 1
                    for col in range(0, 5):
                        worksheet.write(row - 1, col, z[col], classes_format)

    row += 3
    workbook.close()
    xslx_toPdf(lecturer, row)


def get_schedule_items_for_lecturer(lecturer):
    """Function returns every schedule_item connected with specific lecturer."""
    lecturer_items = LecturerItem.objects.filter(lecturer=Profile.objects.get(user=lecturer)).order_by(
        'schedule_item__weekday', 'schedule_item__from_hour')
    schedule_items = []
    for item in lecturer_items:
        schedule_items.append(item.schedule_item)
    return schedule_items
