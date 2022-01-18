# Generated by Django 4.0.1 on 2022-01-18 03:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_profile_academic_degree'),
        ('schedule', '0009_alter_scheduleitem_from_hour_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleitem',
            name='lecture_units',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='lectureritem',
            name='lecturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.profile'),
        ),
        migrations.AlterField(
            model_name='scheduleitem',
            name='from_hour',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scheduleitem',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.schedule'),
        ),
        migrations.AlterField(
            model_name='scheduleitem',
            name='to_hour',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
