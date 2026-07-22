import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='work_start',
            field=models.TimeField(default=datetime.time(9, 0), verbose_name='Начало рабочего дня'),
        ),
        migrations.AddField(
            model_name='master',
            name='work_end',
            field=models.TimeField(default=datetime.time(21, 0), verbose_name='Конец рабочего дня'),
        ),
        migrations.AddField(
            model_name='master',
            name='work_days',
            field=models.CharField(default='0,1,2,3,4,5,6', help_text='Дни недели через запятую: 0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт, 5=Сб, 6=Вс', max_length=20, verbose_name='Рабочие дни'),
        ),
        migrations.AddField(
            model_name='master',
            name='buffer_minutes',
            field=models.PositiveIntegerField(default=0, verbose_name='Буфер между записями (мин)'),
        ),
        migrations.CreateModel(
            name='MasterTimeOff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField(verbose_name='С')),
                ('date_to', models.DateField(verbose_name='По')),
                ('reason', models.CharField(choices=[('vacation', 'Отпуск'), ('sick', 'Больничный'), ('dayoff', 'Выходной'), ('other', 'Другое')], default='dayoff', max_length=20, verbose_name='Причина')),
                ('comment', models.CharField(blank=True, max_length=300, verbose_name='Комментарий')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_off', to='booking.master', verbose_name='Мастер')),
            ],
            options={
                'verbose_name': 'Отсутствие мастера',
                'verbose_name_plural': 'Отсутствия мастеров',
                'ordering': ['-date_from'],
            },
        ),
    ]
