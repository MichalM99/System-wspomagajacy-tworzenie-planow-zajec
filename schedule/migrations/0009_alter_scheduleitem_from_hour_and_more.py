# Generated by Django 4.0.1 on 2022-01-18 02:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_scheduleitem_weekday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleitem',
            name='from_hour',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='scheduleitem',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.schedule'),
        ),
        migrations.AlterField(
            model_name='scheduleitem',
            name='to_hour',
            field=models.TimeField(null=True),
        ),
    ]
