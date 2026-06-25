from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.booking.models import Master


class Review(models.Model):
    client_name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name='Мастер')
    is_published = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.client_name} — {self.rating}/5'
