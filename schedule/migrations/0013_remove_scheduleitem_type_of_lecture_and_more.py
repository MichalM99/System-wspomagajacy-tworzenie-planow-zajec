# Generated by Django 4.0.1 on 2022-01-19 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0012_room_type_of_lecture_scheduleitem_type_of_lecture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduleitem',
            name='type_of_lecture',
        ),
        migrations.AddField(
            model_name='lecture',
            name='type_of_lecture',
            field=models.IntegerField(choices=[(0, 'Laboratorium'), (1, 'Ćwiczenia'), (2, 'Wykład')], default=1, verbose_name='Rodzaj zajęć'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='room',
            name='type_of_lecture',
            field=models.IntegerField(choices=[(0, 'Laboratorium'), (1, 'Ćwiczenia'), (2, 'Wykład')], verbose_name='Rodzaj przewidzianych zajęć'),
        ),
    ]