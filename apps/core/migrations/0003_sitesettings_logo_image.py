from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_sitesettings_email_sitesettings_facebook_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='logo_image',
            field=models.ImageField(blank=True, upload_to='logo/', verbose_name='Логотип (картинка)'),
        ),
    ]
