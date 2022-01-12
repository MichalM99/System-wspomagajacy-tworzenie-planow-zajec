from django.db import models
from django.conf import settings



ACADEMIC_DEGREE = (
    ('Magister', 'Magister'),
    ('Doktor', 'Doktor'),
    ('Doktor habilitowany', 'Doktor habilitowany'),
    ('Profesor nadzwyczajny', 'Profesor nadzwyczajny'),
    ('Profesor zwyczajny', 'Profesor zwyczajny')
)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12, verbose_name='Numer telefonu')
    academic_degree = models.CharField(choices=ACADEMIC_DEGREE, default='magister', max_length=30, verbose_name='Stopień akademicki')
    class Meta:
        verbose_name = 'wykładowca'
        verbose_name_plural = 'wykładowcy'
