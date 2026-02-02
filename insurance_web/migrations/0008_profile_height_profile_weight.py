# Generated manually for profile height/weight

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_web', '0007_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Height (m)'),
        ),
        migrations.AddField(
            model_name='profile',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Weight (kg)'),
        ),
    ]
