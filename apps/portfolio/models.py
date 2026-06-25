from django.db import models
from apps.booking.models import Master


class PortfolioItem(models.Model):
    CATEGORY_CHOICES = [('manicure', 'Маникюр'), ('pedicure', 'Педикюр'), ('design', 'Дизайн')]
    image = models.ImageField(upload_to='portfolio/')
    alt_text = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio', verbose_name='Мастер')
    instagram_post_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Работа'
        verbose_name_plural = 'Портфолио'

    def __str__(self):
        return f'{self.alt_text} ({self.get_category_display()})'
