from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from account.models import Profile


class News(models.Model):
    pub_date = models.DateTimeField()
    headline = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.headline

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'Newsy'
