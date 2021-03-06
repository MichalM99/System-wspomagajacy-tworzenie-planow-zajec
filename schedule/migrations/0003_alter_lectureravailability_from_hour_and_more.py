# Generated by Django 4.0.1 on 2022-01-12 07:08

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_alter_group_options_alter_room_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lectureravailability',
            name='from_hour',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AlterField(
            model_name='lectureravailability',
            name='to_hour',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AlterField(
            model_name='weekday',
            name='weekday',
            field=models.IntegerField(choices=[(0, 'Poniedziałek'), (1, 'Wtorek'), (2, 'Środa'), (3, 'Czwartek'), (4, 'Piątek'), (5, 'Sobota'), (6, 'Niedziela')]),
        ),
    ]
