# Generated by Django 4.0.1 on 2022-01-19 04:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0013_remove_scheduleitem_type_of_lecture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomitem',
            name='schedule_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.scheduleitem'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='schedule_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='nazwa planu'),
        ),
    ]