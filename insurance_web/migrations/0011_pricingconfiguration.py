# Generated manually for PricingConfiguration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_web', '0010_conseillerunavailability'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_base_fee', models.DecimalField(decimal_places=2, default=500.0, help_text='Frais fixes mensuels en euros', max_digits=10, verbose_name='Monthly Base Fee (€)')),
                ('additional_charges_percentage', models.DecimalField(decimal_places=2, default=0.0, help_text='Pourcentage de charges supplémentaires à appliquer (ex: 15 pour 15%)', max_digits=5, verbose_name='Additional Charges Percentage (%)')),
                ('is_active', models.BooleanField(default=True, help_text="Active ou désactive l'application de cette configuration", verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Pricing Configuration',
                'verbose_name_plural': 'Pricing Configurations',
                'ordering': ['-created_at'],
            },
        ),
    ]
