# Generated by Django 4.0.1 on 2022-01-17 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0007_schedule_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleitem',
            name='weekday',
            field=models.IntegerField(choices=[(0, 'Poniedziałek'), (1, 'Wtorek'), (2, 'Środa'), (3, 'Czwartek'), (4, 'Piątek'), (5, 'Sobota'), (6, 'Niedziela')], default=0),
            preserve_default=False,
        ),
    ]
