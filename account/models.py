from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

ACADEMIC_DEGREE = (
    ('Mgr', 'Mgr'),
    ('Dr', 'Dr'),
    ('Dr habilitowany', 'Dr habilitowany'),
    ('Prof. nadzwyczajny', 'Prof. nadzwyczajny'),
    ('Prof. zwyczajny', 'Prof. zwyczajny')
)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12, verbose_name='Numer telefonu')
    academic_degree = models.CharField(choices=ACADEMIC_DEGREE, default='magister',
                                       max_length=30, verbose_name='Stopień akademicki')

    class Meta:
        verbose_name = 'wykładowca'
        verbose_name_plural = 'wykładowcy'

    def __str__(self):
        return self.academic_degree + ' ' + self.user.first_name + ' ' + self.user.last_name

