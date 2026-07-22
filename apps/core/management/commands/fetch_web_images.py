"""Скачивает реальные фото из интернета и расставляет их по сайту.

Запускать НА СЕРВЕРЕ (нужен доступ в интернет):
    python manage.py fetch_web_images --force

Источники (по ключевым словам, без «жёстких» ссылок — поэтому битых нет):
  - loremflickr.com — тематические фото (маникюр, педикюр, ногти, спа);
  - i.pravatar.cc — лица для аватаров отзывов.

Флаг --force перезаписывает уже стоящие картинки (в т.ч. плейсхолдеры из
seed_demo_data). Без флага заполняет только пустые.
"""
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.booking.models import Master, Service
from apps.core.models import SiteSettings
from apps.portfolio.models import PortfolioItem
from apps.reviews.models import Review

CATEGORY_KEYWORDS = {
    'manicure': 'manicure,nails',
    'pedicure': 'pedicure,feet',
    'design': 'nailart,nails',
    'care': 'spa,beauty',
}
DEFAULT_KEYWORDS = 'manicure,nails'


def _download(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if data and len(data) > 1000:  # отсекаем пустые/ошибочные ответы
            return data
    except Exception as exc:
        print(f'    ! не скачалось: {exc}')
    return None


def _flickr(width, height, keywords, seed):
    return f'https://loremflickr.com/{width}/{height}/{keywords}?lock={seed}'


class Command(BaseCommand):
    help = 'Скачивает реальные фото из интернета и ставит их по сайту (hero, мастера, услуги, портфолио, отзывы).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Перезаписать уже стоящие картинки')

    def handle(self, *args, **options):
        force = options['force']

        def need(field):
            return force or not field

        def set_image(obj, field_name, url, filename):
            field = getattr(obj, field_name)
            if not need(field):
                return False
            data = _download(url)
            if not data:
                return False
            getattr(obj, field_name).save(filename, ContentFile(data), save=True)
            return True

        site = SiteSettings.load()
        self.stdout.write('Hero и «О мастере»...')
        set_image(site, 'hero_image', _flickr(1600, 900, 'manicure,beautysalon', 10), 'hero.jpg')
        set_image(site, 'about_image', _flickr(800, 1000, 'manicure,beauty', 11), 'about.jpg')

        self.stdout.write('Мастера...')
        for i, m in enumerate(Master.objects.all()):
            if set_image(m, 'photo', _flickr(600, 600, 'manicure,beautician', 100 + i), f'master_{m.id}.jpg'):
                self.stdout.write(f'  ✓ {m.name}')

        self.stdout.write('Услуги...')
        for i, s in enumerate(Service.objects.all()):
            kw = CATEGORY_KEYWORDS.get(s.category, DEFAULT_KEYWORDS)
            if set_image(s, 'image', _flickr(600, 450, kw, 200 + i), f'service_{s.id}.jpg'):
                self.stdout.write(f'  ✓ {s.name}')

        self.stdout.write('Портфолио...')
        for i, p in enumerate(PortfolioItem.objects.all()):
            kw = CATEGORY_KEYWORDS.get(p.category, DEFAULT_KEYWORDS)
            if set_image(p, 'image', _flickr(600, 600, kw, 300 + i), f'portfolio_{p.id}.jpg'):
                self.stdout.write(f'  ✓ {p.alt_text or p.id}')

        self.stdout.write('Аватары отзывов...')
        for i, r in enumerate(Review.objects.all()):
            if set_image(r, 'avatar', f'https://i.pravatar.cc/200?img={(i % 60) + 1}', f'avatar_{r.id}.jpg'):
                self.stdout.write(f'  ✓ {r.client_name}')

        self.stdout.write(self.style.SUCCESS(
            'Готово. Фото — из интернета (тематические). Портфолио и фото мастеров '
            'позже лучше заменить на реальные работы/лица через админку.'
        ))
