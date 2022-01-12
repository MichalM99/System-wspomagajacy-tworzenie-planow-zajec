from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12)
    academic_deegree = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'wykładowca'
        verbose_name_plural = 'wykładowcy'
