# Generated by Django 5.0.1 on 2024-03-13 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aerc_website', '0017_alter_crypto_options_crypto_name_cryptotransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='crypto',
            name='currency',
            field=models.CharField(default='', max_length=3),
        ),
    ]