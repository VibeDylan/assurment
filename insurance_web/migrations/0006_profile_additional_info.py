# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_web', '0005_alter_prediction_options_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='additional_info',
            field=models.TextField(blank=True, null=True, verbose_name='Additional Information'),
        ),
    ]
