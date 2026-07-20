import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.booking.models import Master, Service, generate_slots_for_master
from apps.core.models import SiteSettings
from apps.portfolio.models import PortfolioItem
from apps.reviews.models import Review

GOLD = (201, 169, 110)
ROSE = (245, 198, 208)
CHOCOLATE = (44, 26, 26)
IVORY = (250, 247, 242)

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def _gradient(width, height, color_a, color_b):
    from PIL import Image
    base = Image.new('RGB', (width, height), color_a)
    top = Image.new('RGB', (width, height), color_b)
    mask = Image.new('L', (width, height))
    mask_data = [int(255 * (x / width)) for x in range(width)] * height
    mask.putdata(mask_data)
    return Image.composite(top, base, mask)


def make_placeholder(filename, width, height, label, color_a=GOLD, color_b=ROSE, font_path=FONT_BOLD, font_size=None):
    from PIL import ImageDraw, ImageFont

    img = _gradient(width, height, color_a, color_b)
    draw = ImageDraw.Draw(img)
    font_size = font_size or max(18, width // 12)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - text_w) / 2 - bbox[0], (height - text_h) / 2 - bbox[1]), label, font=font, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return ContentFile(buf.getvalue(), name=filename)


class Command(BaseCommand):
    help = 'Заполняет сайт демо-контентом (мастера, услуги, портфолио, отзывы) с placeholder-фото, чтобы показать клиенту наполненный сайт.'

    def handle(self, *args, **options):
        settings_obj = SiteSettings.load()
        settings_obj.site_name = 'Aurora Beauty Studio'
        settings_obj.logo_text = 'Aurora'
        settings_obj.phone = '+7 (701) 234-56-78'
        settings_obj.address = 'г. Астана, ул. Байтурсынова 17/1'
        settings_obj.working_hours = 'Пн–Сб: 9:00–21:00, Вс: выходной'
        settings_obj.promo_text = 'Скидка 15% на первое посещение!'
        settings_obj.instagram_url = 'https://www.instagram.com/aurora.beauty'
        settings_obj.whatsapp = '+77012345678'
        settings_obj.telegram = 'aurora.beauty'
        settings_obj.bio = (
            'Aurora Beauty Studio — студия маникюра и педикюра в Астане. '
            'Мы создаём аккуратный, стойкий и стильный нейл-дизайн, используя только '
            'качественные материалы и строго соблюдая стандарты стерилизации. '
            'Каждая клиентка для нас особенная — поэтому мы уделяем время, чтобы '
            'подобрать форму, покрытие и дизайн именно под её образ.'
        )
        settings_obj.years_experience = 7
        settings_obj.clients_count = 1200
        settings_obj.works_count = 850
        settings_obj.email = 'info@aurora-beauty.kz'
        settings_obj.footer_text = 'Все права защищены'
        if not settings_obj.hero_image:
            settings_obj.hero_image = make_placeholder('hero.jpg', 1600, 900, 'Aurora Beauty Studio', GOLD, ROSE)
        if not settings_obj.about_image:
            settings_obj.about_image = make_placeholder('about.jpg', 800, 1000, 'О мастере', CHOCOLATE, GOLD)
        settings_obj.save()
        self.stdout.write(self.style.SUCCESS('Настройки сайта обновлены.'))

        masters_data = [
            ('Алина Ким', 'Мастер маникюра и дизайна ногтей', 'manicure',
             'Более 7 лет создаю аккуратный и стойкий маникюр. Специализируюсь на сложном дизайне и укреплении гелем.'),
            ('Марина Сатпаева', 'Мастер педикюра и SPA-ухода', 'pedicure',
             'Эксперт по аппаратному педикюру и уходу за стопами. Использую только сертифицированные материалы.'),
        ]
        masters = {}
        for name, spec, _, desc in masters_data:
            master, created = Master.objects.get_or_create(
                name=name,
                defaults={'specialization': spec, 'description': desc, 'is_active': True},
            )
            if created:
                generate_slots_for_master(master)
            if not master.photo:
                master.photo = make_placeholder(f'{name.split()[0].lower()}.jpg', 600, 600, name.split()[0], CHOCOLATE, GOLD)
                master.save()
            masters[name] = master
        self.stdout.write(self.style.SUCCESS(f'Мастеров: {Master.objects.count()}'))

        alina = masters['Алина Ким']
        marina = masters['Марина Сатпаева']

        services_data = [
            ('Классический маникюр', 'manicure', 'Аккуратная обработка кутикулы и формы ногтя.', 60, 6000, [alina]),
            ('Маникюр с покрытием гель-лак', 'manicure', 'Маникюр + стойкое покрытие гель-лак на 3 недели.', 90, 9000, [alina]),
            ('Сложный дизайн ногтей', 'design', 'Авторский дизайн: слайдеры, стразы, художественная роспись.', 120, 12000, [alina]),
            ('Укрепление ногтей гелем', 'care', 'Укрепление тонких и слоящихся ногтей биогелем.', 90, 10000, [alina]),
            ('Классический педикюр', 'pedicure', 'Обработка стоп, удаление огрубевшей кожи, покрытие лаком.', 75, 8000, [marina]),
            ('Аппаратный педикюр с покрытием', 'pedicure', 'Аппаратный педикюр + гель-лак.', 100, 12000, [marina]),
            ('SPA-уход для рук', 'care', 'Питательная маска, пилинг, парафинотерапия для рук.', 45, 5000, [alina, marina]),
            ('Дизайн педикюра', 'design', 'Художественный дизайн на педикюре: френч, омбре, стразы.', 110, 11000, [marina]),
        ]
        for order, (name, category, description, duration, price, svc_masters) in enumerate(services_data):
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'category': category, 'description': description,
                    'duration_minutes': duration, 'price_from': price,
                    'is_active': True, 'order': order,
                },
            )
            if not service.image:
                service.image = make_placeholder(f'service_{order}.jpg', 600, 450, name, GOLD, IVORY)
                service.save()
            service.masters.set(svc_masters)
        self.stdout.write(self.style.SUCCESS(f'Услуг: {Service.objects.count()}'))

        portfolio_data = [
            ('Французский маникюр', 'manicure', alina),
            ('Однотонный гель-лак', 'manicure', alina),
            ('Маникюр с втиркой', 'manicure', alina),
            ('Дизайн со стразами', 'design', alina),
            ('Геометрический дизайн', 'design', alina),
            ('Цветочная роспись', 'design', alina),
            ('Классический педикюр', 'pedicure', marina),
            ('Педикюр с покрытием', 'pedicure', marina),
            ('Омбре на педикюре', 'pedicure', marina),
            ('Френч на педикюре', 'pedicure', marina),
            ('Минимализм на ногтях', 'manicure', alina),
            ('Свадебный маникюр', 'design', alina),
        ]
        for i, (alt_text, category, master) in enumerate(portfolio_data):
            if not PortfolioItem.objects.filter(alt_text=alt_text).exists():
                PortfolioItem.objects.create(
                    alt_text=alt_text,
                    category=category,
                    master=master,
                    image=make_placeholder(f'portfolio_{i}.jpg', 600, 600, alt_text, ROSE, GOLD),
                )
        self.stdout.write(self.style.SUCCESS(f'Работ в портфолио: {PortfolioItem.objects.count()}'))

        reviews_data = [
            ('Жанна', 5, 'Очень довольна маникюром! Алина настоящий профессионал, дизайн держался почти месяц.', alina),
            ('Карина', 5, 'Хожу к Марине уже год на педикюр — всегда аккуратно и приятная атмосфера.', marina),
            ('Айгерим', 4, 'Понравился сервис, единственное — пришлось немного подождать своей очереди.', alina),
            ('Динара', 5, 'Лучшая студия в Астане! Стерильно, уютно, мастера внимательные.', alina),
            ('Сабина', 5, 'Сделала свадебный маникюр у Алины — все гости спрашивали, где делала!', alina),
            ('Гульнара', 4, 'Аппаратный педикюр у Марины — стопы как у младенца, рекомендую.', marina),
            ('Жанара', 5, 'Записываюсь уже третий раз, каждый раз результат превосходит ожидания.', alina),
        ]
        for client_name, rating, text, master in reviews_data:
            if not Review.objects.filter(client_name=client_name, text=text).exists():
                Review.objects.create(
                    client_name=client_name, rating=rating, text=text,
                    master=master, is_published=True,
                    avatar=make_placeholder(f'avatar_{client_name}.jpg', 200, 200, client_name[0], CHOCOLATE, ROSE),
                )
        self.stdout.write(self.style.SUCCESS(f'Отзывов: {Review.objects.count()}'))

        self.stdout.write(self.style.SUCCESS(
            'Демо-данные готовы. Фото — сгенерированные placeholder-картинки, '
            'замените их на реальные через админку, когда будут готовы.'
        ))
