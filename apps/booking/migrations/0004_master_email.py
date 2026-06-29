from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_fix_cascade_and_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email для уведомлений о записях'),
        ),
    ]
