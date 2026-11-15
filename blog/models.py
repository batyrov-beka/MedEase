from django.db import models


class ContactRequest(models.Model):
    """Заявка на консультацию с сайта."""

    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=30)
    message = models.TextField('Сообщение', blank=True)
    created_at = models.DateTimeField('Получена', auto_now_add=True)
    is_processed = models.BooleanField('Обработана', default=False)

    class Meta:
        ordering = ['is_processed', '-created_at']
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'

    def __str__(self):
        return f'{self.name} ({self.phone})'
