from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_sitesettings_logo_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='hero_eyebrow',
            field=models.CharField(blank=True, default='Студия красоты · Астана', max_length=120, verbose_name='Надпись над заголовком (hero)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='hero_title',
            field=models.CharField(blank=True, default='Красота в каждой детали', max_length=120, verbose_name='Большой заголовок (hero)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='hero_typeline',
            field=models.CharField(blank=True, default='Мы делаем —', max_length=80, verbose_name='Текст перед бегущими словами (hero)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='service_tags',
            field=models.CharField(blank=True, default='Маникюр, Педикюр, Дизайн ногтей, Наращивание, Гель-лак, Уход', help_text='Показываются в бегущей строке и в анимации «Мы делаем — …»', max_length=300, verbose_name='Ключевые услуги (через запятую)'),
        ),
    ]
