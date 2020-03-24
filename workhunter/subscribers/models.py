from django.db import models
from scraping.views import City, Speciality

class Subscriber(models.Model):
    email = models.CharField(max_length=100, unique=True, verbose_name='E-mail')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, verbose_name='Специальность')
    password = models.CharField(max_length=50, verbose_name='Пароль')
    is_active = models.BooleanField(default=True, verbose_name='Получать рассылку?')


    def __str__(self):
        return self.email

    class Meta:
        managed = True
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
