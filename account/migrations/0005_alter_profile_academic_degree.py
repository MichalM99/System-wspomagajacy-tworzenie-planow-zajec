# Generated by Django 4.0.1 on 2022-01-13 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_profile_academic_deegree_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='academic_degree',
            field=models.CharField(choices=[('Magister', 'Magister'), ('Doktor', 'Doktor'), ('Doktor habilitowany', 'Doktor habilitowany'), ('Profesor nadzwyczajny', 'Profesor nadzwyczajny'), ('Profesor zwyczajny', 'Profesor zwyczajny')], default='magister', max_length=30, verbose_name='Stopień akademicki'),
        ),
    ]
