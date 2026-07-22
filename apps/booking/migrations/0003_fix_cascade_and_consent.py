import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_master_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeslots', to='booking.master', verbose_name='Мастер'),
        ),
        migrations.AddField(
            model_name='booking',
            name='consent_given_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Согласие на обработку ПД дано'),
        ),
    ]
