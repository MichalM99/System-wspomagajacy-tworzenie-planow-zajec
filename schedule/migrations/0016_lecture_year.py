# Generated by Django 4.0.1 on 2022-01-27 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0015_alter_scheduleitem_lecture_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.year'),
        ),
    ]
