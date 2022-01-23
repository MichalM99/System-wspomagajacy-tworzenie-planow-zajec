import os

import xlsxwriter

from schedule.views import xslx_toPdf


def generate_xlsx_personal(lecturer, data_dict, days):
    year_name = str(lecturer).replace(' ', '_').replace('/', '_')
    if os.path.isfile('{}_{}.xlsx'.format(lecturer.id, year_name)):
        return True
    workbook = xlsxwriter.Workbook('{}_{}.xlsx'.format(lecturer.id, year_name))
    worksheet = workbook.add_worksheet()
    headings = [
        'Zajęcia',
        'Od:',
        'Do:',
        'Prowadzący',
        'Sala'
    ]
    # Zajęcia, Od, Do, Prowadzący, Sala

    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'white'})

    main_heading = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter', })

    worksheet.set_column(0, 0, 35)
    worksheet.set_column(1, 2, 8)
    worksheet.set_column(3, 3, 35)
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
