# Generated manually for ConseillerUnavailability

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('insurance_web', '0009_alter_notification_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConseillerUnavailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField(verbose_name='Start')),
                ('end_datetime', models.DateTimeField(verbose_name='End')),
                ('reason', models.CharField(blank=True, choices=[('vacation', 'Vacation'), ('sick', 'Sick leave'), ('training', 'Training'), ('personal', 'Personal'), ('other', 'Other')], default='other', max_length=20, verbose_name='Reason')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conseiller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unavailabilities', to=settings.AUTH_USER_MODEL, verbose_name='Advisor')),
            ],
            options={
                'verbose_name': 'Unavailability',
                'verbose_name_plural': 'Unavailabilities',
                'ordering': ['start_datetime'],
            },
        ),
    ]
